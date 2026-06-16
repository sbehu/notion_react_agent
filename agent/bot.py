import os
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from langchain import hub
from tools.weather import get_weather
from tools.notion_notes import get_notes,add_note
from tools.notion_calendar import get_calendar_events,add_calendar_event,delete_calendar_event

from utils.logger import get_logger

logger=get_logger(__name__)


def get_llm():
    api_key=os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("Groq api key is not set")
        raise ValueError
    
    #return ChatGroq(model="openai/gpt-oss-120b",temperature=0.5,api_key=api_key)
    return ChatGroq(model="llama-3.3-70b-specdec",temperature=0.5,api_key=api_key)

def create_react_agent_custom():
    logger.info("Initialising Agent")
    llm=get_llm()

    tools=[get_weather,get_notes,add_note,get_calendar_events,add_calendar_event,delete_calendar_event]

    try:
        prompt = hub.pull("hwchase17/react")
        agent=create_agent(model=llm,tools=tools,prompt=prompt)
        logger.info("Agent Initialised")
        return agent
    except TypeError as e:
        logger.error(f"Failed to create agent:{e}")
        raise e

