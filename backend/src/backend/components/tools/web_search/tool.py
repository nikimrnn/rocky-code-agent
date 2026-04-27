import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

from backend.components.tools.tool_schema import ToolSchema

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_DESCRIPTION = (
    "The WebSearch tool provides the model with real-time access to the internet, allowing "
    "it to retrieve current information, facts, and data beyond its initial training knowledge."
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
        logger.warning("Permission denied reading '%s'. Using default", path)

    return DEFAULT_DESCRIPTION


class WebSearch(ToolSchema):

    def __init__(self, description_path: str | None = None):
        self.description = load_description(description_path)

        self.api_url = "https://ollama.com/api/web_search"
        self.api_key = os.getenv("OLLAMA_API_KEY")

        if not self.api_key:
            raise ValueError("OLLAMA_API_KEY environment variable is not set.")

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "WebSearch",
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "query"
                    ]
                }
            }
        }

    def _call(self, arguments: dict) -> str:
        query = arguments.get("query")
        if not query:
            return "Error: 'query' argument is missing or empty."

        try:
            response = requests.post(
                self.api_url,
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                },
                json = {
                    "query": str(query)
                },
                timeout = 15
            )

            response.raise_for_status()
            return json.dumps(response.json(), indent=2)

        except requests.exceptions.Timeout:
            logger.error("WebSearch timed out for query: %s", query)
            return "Error: The search request timed out."

        except requests.exceptions.HTTPError as e:
            logger.error("WebSearch HTTP error: %s", e)
            return f"Error: HTTP {response.status_code} - {response.reason}."

        except requests.exceptions.RequestException as e:
            logger.error("WebSearch request failed: %s", e)
            return f"Error: Network error - {e}."
