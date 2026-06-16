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
    # Using Mixtral MoE for significantly better multi-tool context reasoning
    return ChatGroq(model="mixtral-8x7b-32768", temperature=0.2, api_key=api_key)

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

    llm_with_tools = llm.bind_tools(tools)

    # 3. ROBUST SYSTEM PROMPT BLUEPRINT
    system_instructions = (
        "You are a helpful assistant with access to tools for web search, checking weather, "
        "managing Notion notes, and scheduling Notion calendar events. "
        "If the user asks you about current events, specific course details, "
        "or things you do not know from your training data, use the DuckDuckGoSearchRun tool "
        "to find up-to-date information on the web.\n\n"
        
        "CRITICAL NOTION RULES:\n"
        "1. ONLY use the Notion notes tool if the user explicitly uses commands like 'create a note', "
        "'save this to my notes', 'add a task', or 'write a report'.\n"
        "2. NEVER automatically log conversation history, user personal details (like their name or location), "
        "your own thoughts, or general chatter into Notion unless explicitly ordered to do so.\n"
        "3. When using tools to check, update, or delete notes, read the tool's output as a status message only. "
        "NEVER create a new note containing phrases like 'No notes available', 'Success', or 'Database empty'. "
        "Simply reply to the user in plain chat to confirm the action is complete.\n"
        "4. You can only call ONE tool per turn. NEVER invoke multiple search tools or parallel functions in a single response.\n"
        "5. If you need to search the web, choose EITHER DuckDuckGo OR Brave Search, but never both at the same time.\n"
        "6. Wait for the tool output before deciding if you need to take another action.\n\n"

        "NOTION DATABASE DELETION RULES:\n"
        "1. You cannot delete a note/page without knowing its unique 'page_id'.\n"
        "2. If the user commands you to delete a note, you MUST first call 'get_notes' to look up the exact row and grab its 'page_id'.\n"
        "3. Once you find the target ID, immediately pass it into the 'delete_notion_page' tool.\n"
        "4. Do NOT create a new note with confirmation messages or text about the deletion. Just reply to the user in conversational text when finished.\n\n"

        "CALENDAR MANAGEMENT RULES:\n"
        "1. You cannot delete a calendar event without its unique 'event_id'.\n"
        "2. If the user asks you to delete or cancel an event and you do not know the 'event_id', "
        "you MUST first invoke 'get_calendar_events' to find the correct item and its ID.\n"
        "3. Once you find the 'event_id' from the tool output, invoke 'delete_calendar_event' using that ID property.\n"
        "4. If no events match or the schedule is empty, do not invoke any deletion tool; simply tell the user.\n\n"

        "CRITICAL TOOL INSTRUCTION (NO INLINE COMMENTS):\n"
        "When you decide to call a tool/function, you must provide ONLY the clean, valid JSON arguments structure.\n"
        "NEVER append explanations, conversational padding, or inline comments using the '#' symbol inside or directly adjacent to the function arguments payload.\n"
        "For example, do NOT output: {'note': 'text'} # Comment here.\n"
        "Output ONLY the raw JSON object variables. Any extra text or '#' tokens inside the functional call chunk will cause an invalid request error.\n\n"

        "STRICT TOOL MAPPING DIRECTIVES:\n"
        "- If the user asks about notes, tasks, or list content of notes, you MUST ONLY use 'get_notes' or 'add_note'.\n"
        "- If the user asks about calendar, events, schedules, or deleting events, you MUST ONLY use 'get_calendar_events', 'add_calendar_event', or 'delete_calendar_event'.\n"
        "- NEVER call a calendar function when the user is asking about notes.\n"
    )

    memory = MemorySaver()

    try:
        agent = create_react_agent(
            model=llm_with_tools, 
            tools=tools, 
            prompt=system_instructions,
            checkpointer=memory
        )
        logger.info("Agent V3 Initialised successfully with web search capabilities")
        return agent
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise e