from typing import Dict, List, Literal

from fastapi import Request
from jinja2 import Environment, FileSystemLoader

# A simple Jinja2 environment to demonstrate the concept
# In your app, this would be part of your main setup
templates = Environment(loader=FileSystemLoader("templates"), autoescape=True)


def flash_message(
    request: Request,
    message: str,
    message_type: Literal["error", "warning", "success", "info"] = "info",
):
    """Stores a flash message in the session."""
    if "_messages" not in request.session:
        request.session["_messages"] = []

    request.session["_messages"].append(
        {
            "message": message,
            "type": message_type,
        }
    )


def get_flashed_messages(request: Request) -> List[Dict]:
    """Retrieves and clears flash messages from the session."""
    return request.session.pop("_messages", [])
