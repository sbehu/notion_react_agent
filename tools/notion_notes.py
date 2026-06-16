import os
import requests
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def get_notes() -> str:
    """Fetches all recent notes from the user's Notion workspace database."""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_NOTES_DB_ID")

    if not api_key or not db_id:
        return "Error: Notion API key or DB ID not set inside environment configurations."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Query database endpoint
    url = f"https://api.notion.com/v1/databases/{db_id}/query"

    try:
        res = requests.post(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        
        results = data.get("results", [])
        if not results:
            return (
                "System Notice: The Notion notes database was successfully reached, "
                "but it is currently completely empty. Tell the user they don't have "
                "any notes saved yet, and offer to create a new note for them."
            )
            
        # Parse the structured database rows into a readable list for the LLM
        parsed_notes = []
        for page in results:
            properties = page.get("properties", {})
            
            # Match the key structure used in your add_note tool ('Note' column)
            note_prop = properties.get("Note", {}).get("title", [])
            if note_prop:
                text_content = note_prop[0].get("text", {}).get("content", "")
                if text_content:
                    parsed_notes.append(text_content)
                    
        if not parsed_notes:
            return "System Notice: Notes exist in the DB but could not find any text content under the 'Note' column title."

        return f"Found the following saved notes in user's workspace:\n" + "\n".join(f"- {note}" for note in parsed_notes)

    except Exception as e:
        return (
            f"System Error: Unable to fetch notes from Notion right now. "
            f"The API threw this error: {e}. Inform the user gracefully that "
            f"there is a technical connection issue with Notion and try again later."
        )    


@tool
def add_note(note: str) -> str:
    """Add a new note to Notion."""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_NOTES_DB_ID")

    if not api_key or not db_id:
        return "Error: Notion API key or DB ID not set"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Note": {
                "title": [
                    {
                        "text": {
                            "content": note
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": "Pending"
                }
            }
        }
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return f"Note added successfully: '{note}'"
        
    except Exception as e:
        return f"Error adding note to Notion: {str(e)}"