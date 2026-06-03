# crewai-chat-tui

A local, privacy-first conversational AI agent with a terminal UI. Runs entirely on your machine
using [Ollama](https://ollama.com) for inference, [CrewAI](https://crewai.com) for the agent framework,
and [Textual](https://textual.textualize.io) for the TUI. Can be shared to any device on your local network via a
browser using `ttyd`.

```
┌─────────────────────────────────┐
│  Chat History (scrollable)      │
│                                 │
├─────────────────────────────────┤
│  > Input box          [Send]    │
├─────────────────────────────────┤
│  model: llama3.2  KB: 2 files   │
└─────────────────────────────────┘
```

---

## Prerequisites

| Requirement                           | Min version | Notes                |
|---------------------------------------|-------------|----------------------|
| Python                                | 3.11        |                      |
| [uv](https://docs.astral.sh/uv/)      | 0.4+        | Replaces pip         |
| [Ollama](https://ollama.com/download) | latest      | Runs the LLM locally |

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### Install Ollama

Download and install from [ollama.com/download](https://ollama.com/download), then pull the required models:

```bash
# Chat model (used for responses)
ollama pull qwen3.5:4b-q4_K_M

# Memory analysis model (scope/importance inference — much smaller)
ollama pull qwen2.5:0.5b

# Embedding model (used for vector search)
ollama pull nomic-embed-text
```

Verify Ollama is running:

```bash
ollama list   # should show both models
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url> crewai-chat-tui
cd crewai-chat-tui
```

### 2. Create the virtual environment and install dependencies

```bash
uv sync
```

`uv sync` reads `pyproject.toml`, creates a `.venv` in the project directory, and installs all dependencies - no manual
`pip install` needed.

### 3. (Optional) Configure the agent

Edit `config.yaml` to match your environment:

```yaml
ollama:
  base_url: "http://localhost:11434"   # change if Ollama runs on another host
  model: "llama3.2"                    # any model you've pulled with `ollama pull`
  temperature: 0.7

knowledge:
  directory: "knowledge"              # folder of .txt/.md files injected into context
  file_extensions: [ ".txt", ".md" ]

memory:
  storage_path: ".agent_memory"       # persisted inside the project folder

agent:
  name: "LocalAssistant"
  role: "Helpful local AI assistant"
  goal: >
    Answer questions accurately, use the knowledge base when relevant,
    and assist with any task the user brings.
  backstory: >
    You are a knowledgeable assistant running entirely on local hardware. ...

tui:
  title: "Local Agent"
  max_history_lines: 2000

lan:
  ttyd_port: 7681
```

### 4. (Optional) Add knowledge files

Drop `.txt` or `.md` files into the `knowledge/` directory. Their contents are automatically loaded into the agent's
context at startup - useful for domain-specific information, team conventions, or personal notes.

---

## Running

### Local terminal

```bash
uv run python main.py
```

The TUI opens directly in your terminal. Use the keyboard shortcuts below to interact.

### Keyboard shortcuts

| Key      | Action                 |
|----------|------------------------|
| `Enter`  | Send message           |
| `Ctrl+C` | Quit                   |
| `Ctrl+L` | Clear chat history     |
| `Escape` | Cancel current request |

---

## LAN access (browser-based terminal)

Any device on your local network can use the agent through a browser by serving the TUI over HTTP with [
`ttyd`](https://github.com/tsl0922/ttyd).

### Install ttyd

```bash
# macOS
brew install ttyd

# Linux (Debian/Ubuntu)
sudo apt install ttyd

# Or download a binary from https://github.com/tsl0922/ttyd/releases
```

### Start the LAN server

```bash
ttyd -p 7681 uv run python main.py
```

Other devices on the same network can then open:

```
http://<your-machine-ip>:7681
```

To find your machine's local IP:

```bash
# macOS / Linux
ip route get 1 | awk '{print $7}' | head -1
# or
hostname -I | awk '{print $1}'

# macOS alternative
ipconfig getifaddr en0

# Windows
ipconfig | findstr "IPv4"
```

### Keep it running in the background

Use `screen` or `tmux` to keep the server alive after you close your SSH session or terminal:

```bash
# With tmux
tmux new-session -d -s agent 'ttyd -p 7681 uv run python main.py'

# With screen
screen -dmS agent ttyd -p 7681 uv run python main.py
```

To stop it:

```bash
tmux kill-session -t agent
# or
screen -S agent -X quit
```

---

## Project structure

```
crewai-chat-tui/
├── main.py              # Entry point
├── agent.py             # CrewAI agent + crew construction
├── config.py            # YAML config loader
├── config.yaml          # User-editable configuration
├── knowledge.py         # Knowledge base loader
├── knowledge/           # Drop .txt/.md files here
│   ├── about_this_system.md
│   └── team_conventions.txt
├── tools/
│   ├── __init__.py
│   └── system_info.py   # Example tool (currently mocked)
├── tui/
│   ├── __init__.py
│   └── app.py           # Textual TUI application
├── pyproject.toml       # Dependencies (managed by uv)
└── .agent_memory/       # Persisted agent memory (auto-created)
```

---

## Adding tools

1. Copy `tools/system_info.py` and rename the class and `name`/`description`.
2. Implement `_run()` with your logic.
3. Import the new class in `tools/__init__.py` and add it to `ALL_TOOLS`.
4. Pass `ALL_TOOLS` to `tools=` in `agent.py`.

---

## Dependency management with uv

| Task                      | Command                        |
|---------------------------|--------------------------------|
| Install / sync deps       | `uv sync`                      |
| Add a new package         | `uv add <package>`             |
| Remove a package          | `uv remove <package>`          |
| Update all packages       | `uv lock --upgrade && uv sync` |
| Run a command in the venv | `uv run <command>`             |
| Show installed packages   | `uv pip list`                  |

---

## Troubleshooting

**Ollama connection refused**
Ensure Ollama is running: `ollama serve`. Check `base_url` in `config.yaml` matches the host and port.

**`nomic-embed-text` not found**
Pull the embedding model: `ollama pull nomic-embed-text`. This is required for agent memory.

**TUI doesn't render correctly**
Make sure your terminal supports 256 colours and a Unicode-capable font. On macOS, iTerm2 or the default Terminal app
both work fine.

**Browser terminal shows garbled output**
Try a different browser. Chrome and Firefox work best with `ttyd`.

**Port 7681 already in use**
Change `ttyd_port` in `config.yaml` and pass the same port to `ttyd -p <port>`.
