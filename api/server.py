from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from utils.logger import get_logger
from tools.notion_calendar import get_calendar_events, add_calendar_event
from tools.notion_notes import get_notes, add_note
from tools.weather import get_weather
from agent.bot_v3 import create_react_agent_v3

logger = get_logger(__name__)

app = FastAPI(title="ReAct Agent API")

agent = None

@app.on_event("startup")
async def startup_event():
    global agent
    try:
        agent = create_react_agent_v3()
        logger.info("Agent init in API")
    except Exception as e:
        logger.error(f"Failed to Init agent :{e}")
        pass

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None

@app.post("/chat")
async def chat(request: ChatRequest):
    global agent
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not Init")
    
    try:
        # 1. Define a thread configuration for session management
        config = {"configurable": {"thread_id": "static_user_session"}}

        # 2. Invoke the agent and let it complete all tool execution loops
        response = agent.invoke(
            {"messages": [("user", request.message)]},
            config=config
        )

        if isinstance(response, dict) and "messages" in response:
            # 3. Iterate backward to extract the true final assistant summary text
            for msg in reversed(response["messages"]):
                # We target an AIMessage containing a text response that isn't a raw tool call initiation
                if msg.type == "ai" and msg.content and not getattr(msg, "tool_calls", None):
                    return {"response": msg.content}
            
            # Fallback safety capture layer
            last_msg = response["messages"][-1]
            return {"response": last_msg.content}
        
        raise HTTPException(status_code=500, detail="Invalid agent response format")
            
    except Exception as e:
        logger.error(f"Error during chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))    
    
@app.get("/health")
def health():
    return {"status":"ok"}

app.mount("/", StaticFiles(directory="static", html=True), name='static')