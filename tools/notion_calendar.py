import os
import requests
from langchain_core.tools import tool

@tool
def add_calendar_event(date: str, time: str, event: str) -> str:
    """
    This tool will be used to add calendar events in Notion.
    You have to provide date (YYYY-MM-DD), time (HH:MM), event (description).
    CRITICAL RULE: Before calling the add_calendar_event tool, you MUST always call get_calendar_events for that date first to verify the user is not double-booked.
    """
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_CALENDAR_DB_ID")

    if not api_key or not db_id:
        return "Error: Keys not set"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    url = "https://api.notion.com/v1/pages"
    start_datetime = f"{date}T{time}:00+05:30" if time else date

    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Event": {
                "title": [{"text": {"content": event}}]
            },
            "Date": {
                "date": {"start": start_datetime}
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Added Event: {event} at {time} on {date}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_calendar_events(date: str) -> dict:
    """This Tool will get calendar events for a specific date (YYYY-MM-DD) from Notion."""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_CALENDAR_DB_ID")

    if not api_key or not db_id:
        return {"error": "Keys not set"}
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {
        "filter": {
            "property": "Date",
            "date": {"equals": date}
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        events = []
        for page in data.get("results", []):
            event_id = page.get("id")  # Secure the unique row ID field
            props = page.get("properties", {})

            event_title_list = props.get("Event", {}).get("title", [])
            event_name = event_title_list[0].get("text", {}).get("content", "") if event_title_list else "Untitled event"

            time_list = props.get("Time", {}).get("rich_text", [])
            event_time = time_list[0].get("text", {}).get("content", "") if time_list else "All day"

            events.append({
                "event": event_name,
                "time": event_time,
                "event_id": event_id  # Include the explicit UUID key
            })
        return {"events": events, "date": date}
    except Exception as e:
        return {"error": str(e)}

@tool
def delete_calendar_event(event_id: str) -> str:
    """
    Deletes a specific calendar event from Notion using its unique event_id.
    CRITICAL RULE: You must always call get_calendar_events first to look up the correct event_id for the event the user wants to cancel.
    """
    api_key = os.getenv("NOTION_API_KEY")
    
    if not api_key:
        return "Error: Notion API key not set"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    url = f"https://api.notion.com/v1/pages/{event_id}"
    payload = {"archived": True}

    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Successfully deleted event with ID: {event_id}"
    except Exception as e:
        return f"Error executing deletion tool: {str(e)}"