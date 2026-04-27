import json
import argparse
import logging

from backend.components.inference import Inference
from backend.components.tools.web_search.tool import WebSearch
from backend.components.tools.web_fetch.tool import WebFetch
from backend.components.tools.bash.tool import Bash
from backend.components.tools.read_file.tool import ReadFile
from backend.components.tools.write_file.tool import WriteFile

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def build_inference() -> Inference:
    return Inference(
        tools = [
            WebSearch(description_path="./src/backend/components/tools/web_search/description.md"),
            WebFetch(description_path="./src/backend/components/tools/web_fetch/description.md"),
            ReadFile(description_path="./src/backend/components/tools/read_file/description.md"),
            WriteFile(description_path="./src/backend/components/tools/write_file/description.md"),
            Bash(description_path="./src/backend/components/tools/bash/description.md")
        ],
        system_message_path = "./src/backend/system_message.md"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='Ollama Agent', description='A high performative coding agent with useful capabilities to assist engineers with development, code review and debugging.')
    parser.add_argument("--debug", help="Use to debug the agent's conversation histories.", action="store_true")
    return parser

def run(debug: bool = False) -> None:
    inference = build_inference()

    try:
        while True:
            message = input("❯ ").strip()

            if not message:
                continue

            if message.lower() in ["exit", "quit"]: break

            text_started = False

            for chunk in inference.chat(message):
                response = json.loads(chunk)
                block = response.get("block")
                content = response.get("content")

                if block == "text":
                    if not text_started:
                        print("\n● ", end="")
                        text_started = True
                    print(content, end='', flush=True)

                elif block == "tool_calls":
                    for call in content:
                        name = call["function"]["name"]
                        args = call["function"]["arguments"]
                        print(f"\n○ {name}({args})")

                elif block == "error":
                    print(f"✗ Error: {content}")
                    logger.error("Agent error block received: %s", content)

            print("\n")

            if debug:
                print("\nConversation History:\n")
                print(json.dumps(inference.messages, indent=4))

    except KeyboardInterrupt:
        print("\n\nBye-bye!!!")

if __name__ == "__main__":
    args = build_parser().parse_args()
    run(debug=args.debug)
