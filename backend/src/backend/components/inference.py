import ollama
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_MESSAGE = (
    "You are an expert in Application Security Research and Application development. "
    "You operate with a mindset of 'Trust, but Verify.' You don't just write code; "
    "you analyze its security implications, performance bottlenecks, and edge cases. "
    "You are comfortable with low-level systems, web security, and AI orchestration."
)

def load_system_message(path: str | None) -> str:
    """Load system message from file, falling back to default with a warning."""
    if not path:
        return DEFAULT_SYSTEM_MESSAGE

    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("System message file not found at '%s'. Using default.", path)
    except PermissionError:
        logger.warning("Permission denied reading '%s'. Using default.", path)

    return DEFAULT_SYSTEM_MESSAGE

class Inference:

    def __init__(self, tools: list | None = None, system_message_path: str | None = None):
        model = os.getenv("MODEL")

        if not model:
            raise ValueError("MODEL environment variable is not set.")

        self.model = model
        self.messages: list[dict] = [
            {
                "role": "system",
                "content": load_system_message(system_message_path)
            }
        ]
        self.tools = tools or []
        self.tool_map = {
            tool.get_schema()["function"]["name"]: tool for tool in self.tools
        }

    def chat(self, message: str, max_turns: int = 100):
        """
        Generator that yields JSON-encoded event blocks:
            {"block": "text", "content": str}
            {"block": "tool_calls", "content": list}
            {"block": "error", "content": str}
        """

        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )


        for turn in range(max_turns):
            think_block = ''
            text_block = ''
            tools_block = []

            try:
                generator = ollama.chat(
                    model = self.model,
                    messages = self.messages,
                    tools = [
                        tool.get_schema() for tool in self.tools
                    ],
                    stream = True
                )
            except Exception as e:
                logger.exception("Ollama chat failed on turn %d", turn)
                yield json.dumps(
                    {
                        "block": "error",
                        "content": str(e)
                    }
                )

            for chunk in generator:
                if chunk.message.thinking:
                    think_block += chunk.message.thinking

                if chunk.message.content:
                    text_block += chunk.message.content
                    yield json.dumps(
                        {
                            "block": "text",
                            "content": chunk.message.content
                        }
                    )

                if chunk.message.tool_calls:
                    for call in chunk.message.tool_calls:
                        tools_block.append(call.model_dump())

            self.messages.append(
                {
                    "role": "assistant",
                    "thinking": think_block,
                    "tool_calls": tools_block,
                    "content": text_block
                }
            )

            if not tools_block:
                break

            yield json.dumps(
                {
                    "block": "tool_calls",
                    "content": tools_block
                }
            )

            for call in tools_block:
                name = call["function"]["name"]
                arguments = call["function"]["arguments"]

                if name not in self.tool_map:
                    msg = f"Tool '{name}' not found in tool_map."
                    logger.error(msg)
                    yield json.dumps(
                        {
                            "block": "error",
                            "content": msg
                        }
                    )
                    return

                result = self.tool_map[name]._call(arguments)
                self.messages.append(
                    {
                        "role": "tool",
                        "content": result
                    }
                )

        else:
            msg = f"Reached max_turns limit ({max_turns})."
            logger.warning(msg)
            yield json.dumps(
                {
                    "block": "error",
                    "content": msg
                }
            )
