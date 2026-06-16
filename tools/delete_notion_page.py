import os
import requests
from langchain_core.tools import tool

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@tool
def delete_notion_page(page_id: str) -> str:
    """
    Deletes or archives a specific page/note from a Notion database using its unique page_id.
    You must discover the page_id by listing or searching notes first before calling this.
    """
    # Notion treats deletion as updating the 'archived' boolean state to true
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"archived": True}
    
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return f"Success: Note with ID {page_id} has been completely removed."
        else:
            return f"Failed to delete page. Status code: {response.status_code}, Details: {response.text}"
    except Exception as e:
        return f"Error executing page deletion: {str(e)}"
    


