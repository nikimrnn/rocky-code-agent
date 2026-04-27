# Rocky - A terminal coding agent

Rocky is a terminal-first AI agent built from scratch as a personal experiment with open-weight models. The goal is to explore how far open-weight models can go as a practical engineering assistant, when given the right capabilities -- handling reals tasks like reading and writing files, searching the web, executing shell commands in a persistent sandboxed bash session, and reasoning through multi-step problems. The intention as well to replicate capabilities similar to Claude Code, understanding context window and optimization strategies, and exploring efficiency improvements (e.g., prompt design, tool usage, prompt caching)

No frameworks are used for orchestration -- all agent behavior is implemented via direct LLM API interaction with Ollama API Python library.

---

## Overview

Rocky is not a chatbot. It is an **agentic system**.

It reasons through tasks, selects tools, and executes multi-step workflows within a persistent environment. It can:

- Inspect and modify local codebases
- Search and retrieve external information
- Execute shell commands
- Chain actions across multiple steps

---

## Model

For development purposes, Rocky runs on `gpt-oss:120b-cloud` served on the cloud through Ollama. The model supports native tool calling and extended thinking, both of which the Rocky takes advantage of. You can swap the model by modifying the `MODEL` in `.env` file -- any Ollama model with tool-calling and reasoning should work.

For more list of Ollama models with tool-calling and reasoning capabilities, you can find it here: https://ollama.com/search?c=thinking&c=cloud&c=tools&o=newest

---

## Features

- **Autonomous tool usage**  
  The model selects and chains tools based on task requirements

- **Persistent execution environment**  
  Bash session, filesystem state, and context persist across steps

- **Web intelligence pipeline**  
  Search → fetch → analyze workflow for external information

- **Direct filesystem access**  
  Reads and writes local files with controlled boundaries

- **Streaming output**  
  Token-by-token response streaming in terminal

- **Thinking trace capture**  
  Model reasoning is stored (UI rendering planned)

- **Debug mode**  
  Full conversation trace printed after each turn

- **Fully local execution**  
  No external inference; all processing via Ollama

---

## Current Limitations

- No full UI (CLI only)
- Streaming mode does **not support Markdown rendering**. Python `rich` library does not support rendering streamed Markdown content.
- Tool execution is powerful but not yet sandboxed
- No persistent conversation history

---

## Tools

| Tool        | Purpose |
|-------------|---------|
| `WebSearch` | Retrieve URLs and high-level summaries |
| `WebFetch`  | Extract full content from a known URL |
| `ReadFile`  | Read a file from the local filesystem |
| `WriteFile` | Create or overwrite files |
| `Bash`      | Execute shell commands (last resort) |

`WebSearch` requires an Ollama API key set as the OLLAMA_API_KEY environment variable in the `.env` file.

### Tool Design Principles

- Tools are **strictly scoped**
- The agent must use the **most specific tool available**
- Tool misuse is considered failure
- Bash is **intentionally restricted** to prevent overreach

---

## Project Structure
```
backend/
├── src/
│   └── backend/
│       ├── app.py                # CLI entry point
│       ├── system_message.md     # Agent rules, constraints, and behavior
│       └── components/
│           ├── inference.py      # Agent loop and LLM interaction
│           └── tools/            # Tools specification
│               ├── tool_schema.py
│               ├── bash/
│               ├── web_search/
│               ├── web_fetch/
│               ├── read_file/
│               └── write_file/
├── tests/
├── pyproject.toml
└── requirements.txt
```

Each tool contains:
- `tool.py` → execution logic
- `description.md` → instructions for the model

---

## Prerequisites

- [Ollama](https://ollama.com/search?c=thinking&c=cloud&c=tools&o=newest) with your chosen model, pulled locally or served from cloud.
- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended)

---

## Setup

### 1. Clone repository
```bash
git clone https://github.com/nikimrnn/rocky-code-agent.git
cd rocky-code-agent/backend
```

### 2. Install dependencies
```bash
uv sync
```

### 3. Configure environment

Create `.env` in `backend/`:

```env
MODEL=qwen3.5:14b

# Required for WebSearch
OLLAMA_API_KEY=your_api_key_here
```

The agent will fail fast if required variables are missing.

---

## Usage

### Run agent
```bash
uv run python -m app
```

### Debug mode
```bash
uv run python -m app --debug
```

### Example
```
❯ What vulnerabilities should I look for in this Flask app? Read the main entry point first. 

○ ReadFile({'path': 'src/app.py'}) 

● I can see a few potential issues worth investigating... 1. The secret key is hardcoded — this should be loaded from an environment variable. 2. The /upload route has no file type validation, which could allow arbitrary file uploads. 3. Debug mode is enabled in production (debug=True), which exposes the interactive debugger
```

---

## Contributing

To add a tool:

1. Create a new directory under `tools/`
2. Implement `tool.py` using `ToolSchema`
3. Add `description.md` with clear usage rules
4. Register the tool in `app.py`

### Rules
- Tools must be single-purpose
- Tool descriptions must be unambiguous
- Errors must be returned as strings, not exceptions

---

## Roadmap

- [ ] Slash commands (`/quit`, `/clear`, `/model`, etc.)
- [ ] Context window optimization
- [ ] AskUser confirmation tool
- [ ] React Ink terminal UI with markdown rendering
- [ ] Persistent conversation storage
- [ ] MCP support
- [ ] Tool permission system / sandboxing
- [ ] Tool test suite
- [ ] Prompt caching

---

## License

MIT
