"""Upload meeting summaries to Craft via its REST API."""

import os
from datetime import datetime, timezone

import httpx

MEETINGS_FOLDER_TITLE = "Meetings"


def _get_config() -> tuple[str, str]:
    """Return (api_url, api_key) from environment variables."""
    api_url = os.environ.get("CRAFT_API_URL")
    if not api_url:
        raise RuntimeError("CRAFT_API_URL environment variable is not set")
    api_key = os.environ.get("CRAFT_API_KEY")
    if not api_key:
        raise RuntimeError("CRAFT_API_KEY environment variable is not set")
    return api_url, api_key


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def find_meetings_document(client: httpx.Client) -> str:
    """Find the 'Meetings' document and return its ID.

    Raises RuntimeError if not found.
    """
    response = client.get("/documents")
    response.raise_for_status()
    documents = response.json()["items"]
    for doc in documents:
        if doc["title"] == MEETINGS_FOLDER_TITLE and not doc.get("isDeleted", False):
            return doc["id"]
    raise RuntimeError(
        f"No '{MEETINGS_FOLDER_TITLE}' document found in Craft workspace"
    )


def create_subpage(client: httpx.Client, parent_id: str, title: str) -> str:
    """Create a sub-page block inside a parent page. Returns the new page ID."""
    response = client.post(
        "/blocks",
        json={
            "blocks": [
                {
                    "type": "page",
                    "textStyle": "card",
                    "markdown": title,
                }
            ],
            "position": {"position": "end", "pageId": parent_id},
        },
    )
    response.raise_for_status()
    return response.json()["items"][0]["id"]


def insert_content(client: httpx.Client, page_id: str, markdown: str) -> None:
    """Insert markdown content into a page."""
    response = client.post(
        "/blocks",
        json={
            "markdown": markdown,
            "position": {"position": "end", "pageId": page_id},
        },
    )
    response.raise_for_status()


def upload_to_craft(title: str, content: str) -> str:
    """Create a dated meeting note in the Craft Meetings folder.

    Args:
        title: Short title for the meeting note.
        content: Markdown content (the summary).

    Returns:
        The dated title that was created.
    """
    api_url, api_key = _get_config()
    dated_title = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')} {title}"

    with httpx.Client(base_url=api_url, headers=_headers(api_key)) as client:
        meetings_id = find_meetings_document(client)
        page_id = create_subpage(client, meetings_id, dated_title)
        insert_content(client, page_id, content)

    return dated_title
