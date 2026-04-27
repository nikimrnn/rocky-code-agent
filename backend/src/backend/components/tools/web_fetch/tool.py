import requests
from pathlib import Path
import os
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse

from backend.components.tools.tool_schema import ToolSchema

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_DESCRIPTION = (
    "The WebFetch tool allows the model to retrieve the full text content of a specific"
    "webpage by its URL, enabling deep reading and analysis of online articles, "
    "documentation, or reports."
)

def load_description(path: str | None) -> str:
    """Load tool description from file, falling back to default with a warning."""

    if not path:
        return DEFAULT_DESCRIPTION

    try:
        return Path(path).read_text(encoding="utf-8").strip()

    except FileNotFoundError:
        logger.warning("Tool description file not found at '%s'. Using default.", path)

    except PermissionError:
        logger.warning("Permission denied reading '%s'. Using default.", path)

    return DEFAULT_DESCRIPTION


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


class WebFetch(ToolSchema):

    def __init__(self, description_path: str | None = None):
        self.description = load_description(description_path)

        self.api_url = "https://r.jina.ai/"

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "WebFetch",
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "url"
                    ]
                }
            }
        }

    def _call(self, arguments: dict) -> str:

        url = arguments.get("url")

        if not url:
            return "Error: 'url' argument is missing or empty."

        if not is_valid_url(url):
            return f"Error: Invalid URL '{url}'. Must include a valid scheme (http/https) and domain."

        try:
            response = requests.get(
                f"{self.api_url}/{str(url)}",
                timeout = 15
            )
            response.raise_for_status()
            return response.text

        except requests.exceptions.HTTPError as e:
            logger.error("WebFetch HTTP error: %s", e)
            return f"Error: HTTP {response.status_code} - {response.reason}."

        except requests.exceptions.Timeout:
            logger.error("WebFetch timed out for URL: %s", url)
            return "Error: The fetch request timed out"

        except requests.exceptions.RequestException as e:
            logger.error("WebFetch request failed: %s", e)
            return f"Error: Network error - {e}."
