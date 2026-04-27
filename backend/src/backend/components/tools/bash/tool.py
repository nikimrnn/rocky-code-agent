import subprocess
import threading
import queue
import shlex
import uuid
import os
import logging
from pathlib import Path

from backend.components.tools.tool_schema import ToolSchema

logger = logging.getLogger(__name__)

DEFAULT_DESCRIPTION = (
    "The Bash tool executes shell commands in a persistent bash session. "
    "Use this tool for system operations, file discovery, environment management, "
    "and anything requiring direct shell access."
)

# Commands the agent is permitted to run as the entry executable.
# Extend this list as your use cases grow.
ALLOWED_COMMANDS = {
    "ls", "cat", "echo", "pwd", "grep", "find", "wc", "head", "tail",
    "sed", "mv", "cp", "mkdir", "rm", "touch", "chmod",
    "bun", "node", "npm", "python3", "pip", "uv",
    "git", "gh",
    "curl", "wget",
    "jq", "xargs", "env", "export", "which", "type",
}

# Shell operators that are explicitly blocked regardless of allow-list.
BLOCKED_OPERATORS = {"&&", "||", ";", "&"}

# Characters blocked anywhere in a token to prevent injection.
FORBIDDEN_CHARS = {"`", "$("}


def load_description(path: str | None) -> str:
    if not path:
        return DEFAULT_DESCRIPTION
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        logger.warning("Tool description file not found at '%s'. Using default.", path)
    except PermissionError:
        logger.warning("Permission denied reading '%s'. Using default.", path)
    return DEFAULT_DESCRIPTION


class Bash(ToolSchema):

    def __init__(self, description_path: str | None = None, timeout: float = 30.0):
        self.timeout = timeout
        self.description = load_description(description_path)

        self.process = subprocess.Popen(
            ["/bin/bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
        )

        self.output_queue: queue.Queue = queue.Queue()
        self.error_queue: queue.Queue = queue.Queue()
        self._start_readers()

    def _start_readers(self) -> None:
        """Start daemon threads to drain stdout and stderr into queues."""
        def reader(pipe, q: queue.Queue) -> None:
            try:
                for line in iter(pipe.readline, ""):
                    q.put(line)
            except Exception:
                pass
            finally:
                pipe.close()

        threading.Thread(
            target=reader, args=(self.process.stdout, self.output_queue), daemon=True
        ).start()
        threading.Thread(
            target=reader, args=(self.process.stderr, self.error_queue), daemon=True
        ).start()

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "Bash",
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute.",
                        }
                    },
                    "required": ["command"],
                },
            },
        }

    @classmethod
    def _validate_command(cls, command: str) -> tuple[bool, str | None]:
        """Validate command against the allow-list and forbidden patterns."""
        if not command or not command.strip():
            return False, "No command given."

        try:
            tokens = shlex.split(command)
        except ValueError as e:
            return False, f"Could not parse command: {e}."

        if not tokens:
            return False, "No command given."

        executable = tokens[0]
        if executable not in ALLOWED_COMMANDS:
            return False, f"Command '{executable}' is not in the allow-list."

        for token in tokens[1:]:
            if token in BLOCKED_OPERATORS:
                return False, f"Operator '{token}' is not permitted."
            for pattern in FORBIDDEN_CHARS:
                if pattern in token:
                    return False, f"Token '{token}' contains a forbidden pattern '{pattern}'."

        return True, None

    def _call(self, arguments: dict) -> str:
        command = arguments.get("command")

        if not command:
            return "Error: 'command' argument is missing or empty."

        is_valid, error_msg = self._validate_command(command)
        if not is_valid:
            return f"Security Error: {error_msg}"

        sentinel = f"__END_{uuid.uuid4().hex}__"

        try:
            self.process.stdin.write(f"{command}; echo '{sentinel}'\n")
            self.process.stdin.flush()

            output_buffer = []
            while True:
                try:
                    line = self.output_queue.get(timeout=self.timeout)
                    if sentinel in line:
                        break
                    output_buffer.append(line)
                except queue.Empty:
                    return f"Error: Command timed out after {self.timeout}s."

            err_buffer = []
            while not self.error_queue.empty():
                err_buffer.append(self.error_queue.get_nowait())

            result = "".join(output_buffer).strip()
            errors = "".join(err_buffer).strip()

            if errors:
                return f"Output:\n{result}\nErrors:\n{errors}"
            return result if result else "Command executed successfully (no output)."

        except Exception as e:
            logger.exception("Bash execution error for command: %s", command)
            return f"Execution Error: {e}."

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        """Explicitly terminate the bash subprocess."""
        if hasattr(self, "process") and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
