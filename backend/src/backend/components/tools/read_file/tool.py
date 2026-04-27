from pathlib import Path
import logging

from backend.components.tools.tool_schema import ToolSchema


logger = logging.getLogger(__name__)

DEFAULT_DESCRIPTION = (
    "The ReadFile tool enables the model to retrieve the content of specific files"
    "from the filesystem, providing the necessary context for analysis, debugging,"
    "or data extraction."
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


class ReadFile(ToolSchema):

    def __init__(self, description_path: str | None = None):
        self.description = load_description(description_path)

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "ReadFile",
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "path"
                    ]
                }
            }
        }

    def _call(self, arguments: dict) -> str:
        path = arguments.get("path")

        if not path:
            return "Error: 'path' argument is missing or empty."

        try:
            return Path(path).read_text(encoding="utf-8").strip()

        except FileNotFoundError:
            logger.error("File not found at '%s'.", path)
            return f"Error: The file '{path}' was not found."

        except PermissionError:
            logger.error("Permission denied reading '%s'.", path)
            return f"Error: Permission denied reading {path}."

        except IsADirectoryError:
            logger.error("Path '%s' is a directory, not a file.", path)
            return f"Error: '{path}' is a directory, not a file."
