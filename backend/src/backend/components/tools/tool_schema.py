from abc import ABC, abstractmethod


class ToolSchema(ABC):
    """
    Base contract for all agent tools.

    Subclasses must implement:
        - get_schema(): returns the Ollama-compatible function schema dict
        - _call(): executes the tool and returns a string result
    """

    @abstractmethod
    def get_schema(self) -> dict:
        """Return the Ollama-compatible JSON schema describing the tool."""
        pass

    @abstractmethod
    def _call(self, arguments: dict) -> str:
        """Execute the tool with the given arguments and return a string result."""
        pass
