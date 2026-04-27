from pathlib import Path
import logging

from backend.components.tools.tool_schema import ToolSchema


logger = logging.getLogger(__name__)

DEFAULT_DESCRIPTION = (
    "The WriteFile tool enables the model to create new files or overwrite existing ones with specific content."
    "This is a primary tool for code generation, configuration management and persisting data within the local"
    "environment."
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


class WriteFile(ToolSchema):

    def __init__(self, description_path: str | None = None):
        self.description = load_description(description_path)

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "WriteFile",
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string"
                        },
                        "content": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "path",
                        "content"
                    ]
                }
            }
        }

    def _call(self, arguments: dict) -> str:

        path = arguments.get("path")
        content = arguments.get("content")

        if not path or not content:
            return "Error: 'path' and 'content' arguments are required."


        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content_written = file_path.write_text(content, encoding="utf-8")
            return f"Successfully wrote {content_written} content to '{path}'."

        except PermissionError:
            logger.error("Permission denied writing to '%s'.", path)
            return f"Error: Permission denied writing to '{path}'."

        except IsADirectoryError:
            logger.error("Path '%s' is a directory, not a file.", path)
            return f"Error: '{path}' is a directory, not a file."

        except OSError as e:
            logger.error("Failed to write to '%s': %s", path, e)
            return f"Error: Could not write to '{path}' — {e}."
