import os
import logging
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# 1. CLEAN TOOL IMPORTS
from tools.delete_notion_page import delete_notion_page
from langchain_community.tools import DuckDuckGoSearchRun
from tools.notion_notes import get_notes, add_note
from tools.weather import get_weather
from tools.notion_calendar import get_calendar_events, add_calendar_event, delete_calendar_event

logger = logging.getLogger(__name__)

# Instantiate global tools
web_search_tool = DuckDuckGoSearchRun()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("Groq api key is not set")
        raise ValueError
    
    # Swapped to the production standard 70B parameter model for complex multi-tool reliability
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, api_key=api_key)

def create_react_agent_v3():
    logger.info("Initialising Fresh Agent V3 with Memory and Web Search")
    llm = get_llm()

    # 2. MASTER TOOLS LIST REGISTERED TO THE ENGINE
    tools = [
        web_search_tool,       
        get_weather,
        get_notes,             # For listing/searching note records and extracting page_ids
        add_note,              # For creating text rows
        delete_notion_page,    # Connected custom deletion tool
        get_calendar_events,
        add_calendar_event,
        delete_calendar_event
    ]

    # 3. STREAMLINED SYSTEM PROMPT STRING
    system_instructions = (
        "You are an AI assistant with access to tools for web search, weather, notes, and calendar management.\n\n"
        
        "CRITICAL TOOL CALLING FORMAT:\n"
        "- You must use native tool calling syntax. NEVER wrap your function calls or arguments in text tags like '<function>' or brackets.\n"
        "- Do NOT include inline comments using '#' inside or near the function arguments payload.\n\n"

        "NOTION NOTES RULES:\n"
        "1. Only use note tools if explicitly asked to manage notes.\n"
        "2. To delete a note, you MUST first call 'get_notes' to find the target item, copy its real 'page_id' UUID string, and pass it directly into 'delete_notion_page'.\n\n"

        "CALENDAR RULES:\n"
        "1. To cancel or delete an event, you MUST first call 'get_calendar_events' for that specific date, locate the item, copy its 'event_id' UUID string, and pass it into 'delete_calendar_event'.\n\n"
        
        "GENERAL UTILITIES:\n"
        "- Use DuckDuckGoSearchRun for current events or real-time information you do not know.\n"
        "- Call only ONE tool per turn. Wait for the tool response before making any decisions."
    )

    memory = MemorySaver()

    try:
        agent = create_react_agent(
            model=llm, 
            tools=tools, 
            prompt=system_instructions,
            checkpointer=memory
        )
        logger.info("Agent V3 Initialised successfully with compatible prompt string")
        return agent
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise e