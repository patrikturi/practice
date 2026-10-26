# knowledge-mcp

A progressive **Model Context Protocol (MCP)** learning project for full-stack developers.

You build a **personal knowledge-base server** in Python 3.14 with:

- **UV** for project/env management
- Official **`mcp` SDK v2** (`MCPServer`)
- **Pydantic** for tool/resource payloads
- **SQLite** for persistence
- **httpx** to import a URL as a note

Follow the curriculum in [LEARNING.md](LEARNING.md).

## Requirements

- [UV](https://docs.astral.sh/uv/) installed
- Python 3.14 (UV will use `.python-version`)
- Optional: Node.js/`npx` for MCP Inspector (`uv run mcp dev ...`)

## Quick start

```bash
cd /Users/patrik/.patrik/practice/mcp_server
uv sync
uv run pytest
uv run python client/demo_client.py
```

### MCP Inspector

```bash
uv run mcp dev src/knowledge_mcp/server.py
```

Open the printed URL → Tools / Resources / Prompts.

### Run the server

```bash
# stdio (default) — what Cursor launches for you
uv run python -m knowledge_mcp

# Streamable HTTP — you start it; clients connect to the URL
uv run python -m knowledge_mcp --transport streamable-http --port 8000
# endpoint: http://127.0.0.1:8000/mcp
```

## Use in Cursor (local)

Cursor can talk to this server on your machine.

### Option A — stdio (recommended)

Cursor starts the process; you do **not** leave a terminal running.

1. Open Cursor Settings → MCP (or add project config).
2. Merge the `knowledge-mcp` entry from [examples/cursor.mcp.json](examples/cursor.mcp.json).
3. Adjust `--directory` / `KNOWLEDGE_MCP_DB` paths if your clone lives elsewhere.
4. Reload MCP / restart Cursor Agent.

Then ask Agent to create or search notes.

### Option B — Streamable HTTP

```bash
uv run python -m knowledge_mcp --transport streamable-http --port 8000
```

Point Cursor at `http://127.0.0.1:8000/mcp` (see `knowledge-mcp-http` in the example config).

## Environment

| Variable | Meaning | Default |
|----------|---------|---------|
| `KNOWLEDGE_MCP_DB` | SQLite database file path | `./data/notes.db` |

## Project layout

```
src/knowledge_mcp/
  server.py      # MCPServer + CLI transports
  models.py      # Pydantic models
  db.py          # SQLite repository
  tools.py       # MCP tools
  resources.py   # notes://list, note://{id}
  prompts.py     # summarize_note, weekly_review
client/demo_client.py
tests/
LEARNING.md
examples/cursor.mcp.json
```

## Tools at a glance

| Tool | Purpose |
|------|---------|
| `ping` | Health check |
| `create_note` | Create a validated note |
| `get_note` / `list_notes` / `search_notes` / `delete_note` | CRUD + search |
| `import_url` | Fetch a page with httpx and store as a note |

## License

Learning / practice project — use freely.
