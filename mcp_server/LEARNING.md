# Learning path: MCP knowledge base

This project is one growing codebase. Each step adds concepts you can verify with MCP Inspector, Cursor, or the demo client.

Prereq: `uv sync` from the repo root.

---

## Step 1 — Hello MCP tool

**Goal:** Run a minimal MCP server and call one tool.

**Concepts:**
- MCP host (Cursor / Inspector) vs MCP server
- Tools = actions the model can invoke
- stdio transport: host spawns your process and speaks over stdin/stdout

**Where in code:**
- [`src/knowledge_mcp/server.py`](src/knowledge_mcp/server.py) — `MCPServer("knowledge-mcp")`
- [`src/knowledge_mcp/tools.py`](src/knowledge_mcp/tools.py) — `ping`

**Try it:**
```bash
uv run mcp dev src/knowledge_mcp/server.py
```
Call `ping` → expect `pong from knowledge-mcp`.

**Checkpoint:** Inspector lists `ping` and returns a successful result.

---

## Step 2 — Pydantic-validated tools

**Goal:** Let the SDK generate JSON Schema from Pydantic models and type hints.

**Concepts:**
- `BaseModel` / `Field` / `Annotated` become the tool input schema
- Invalid input fails before your handler logic
- Structured tool results (models serialize cleanly)

**Where in code:**
- [`src/knowledge_mcp/models.py`](src/knowledge_mcp/models.py) — `NoteCreate`, `Note`, `NoteSearchQuery`
- `create_note` takes a nested `note: NoteCreate` object

**Try it:**
In Inspector, call `create_note` with:
```json
{
  "note": {
    "title": "First note",
    "body": "Hello schema",
    "tags": ["mcp"],
    "priority": "high"
  }
}
```
Then try an invalid tag like `"Bad Tag!"` and observe validation failure.

**Checkpoint:** Valid create returns a `Note` with `id` / timestamps; invalid payloads are rejected.

---

## Step 3 — Resources

**Goal:** Expose read-only context via URIs.

**Concepts:**
- Tools = do something; resources = read something
- Static URI: `notes://list`
- Templated URI: `note://{note_id}`

**Where in code:**
- [`src/knowledge_mcp/resources.py`](src/knowledge_mcp/resources.py)

**Try it:**
1. Create a note with `create_note`.
2. Read `notes://list`.
3. Read `note://<id>` from the list.

**Checkpoint:** Resource text includes the note title and body without calling a tool.

---

## Step 4 — Prompts

**Goal:** Ship user-triggered message templates.

**Concepts:**
- Prompts are chosen by a person (slash command / menu), not auto-picked like tools
- Return `str` or a list of `UserMessage` / `AssistantMessage`

**Where in code:**
- [`src/knowledge_mcp/prompts.py`](src/knowledge_mcp/prompts.py) — `summarize_note`, `weekly_review`

**Try it:**
Inspector → Prompts → `summarize_note` with a real `note_id`.

**Checkpoint:** Rendered messages include the note title/body and steer a summary.

---

## Step 5 — Persistence + URL import

**Goal:** Survive restarts and reach the network.

**Concepts:**
- Thin SQLite repository (no ORM) behind tools/resources
- `KNOWLEDGE_MCP_DB` for the file path
- `httpx` for outbound HTTP from a tool

**Where in code:**
- [`src/knowledge_mcp/db.py`](src/knowledge_mcp/db.py)
- Tools: `list_notes`, `search_notes`, `delete_note`, `import_url`

**Try it:**
```bash
export KNOWLEDGE_MCP_DB="$PWD/data/notes.db"
uv run mcp dev src/knowledge_mcp/server.py
```
Create a note, restart Inspector, `list_notes` again.  
Optionally call `import_url` with a public docs URL.

**Checkpoint:** Notes remain after restart; search by tag/text works.

---

## Step 6 — Streamable HTTP transport

**Goal:** Serve the same tools over HTTP.

**Concepts:**
- stdio = local subprocess (Cursor default)
- `streamable-http` = listen on a port (`/mcp` by default)
- Transport is chosen in `mcp.run(...)`, not in `MCPServer(...)`

**Where in code:**
- [`src/knowledge_mcp/server.py`](src/knowledge_mcp/server.py) — `--transport` CLI

**Try it:**
```bash
uv run python -m knowledge_mcp --transport streamable-http --port 8000
uv run python client/demo_client.py --mode http --http http://127.0.0.1:8000/mcp
```

**Checkpoint:** Demo client prints tools while the HTTP server is running.

---

## Step 7 — MCP client + tests

**Goal:** Call your server from Python like any host would.

**Concepts:**
- `Client(server)` — in-memory (great for tests)
- `Client(StdioServerParameters(...))` — subprocess, Cursor-like
- `Client("http://...")` — Streamable HTTP

**Where in code:**
- [`client/demo_client.py`](client/demo_client.py)
- [`tests/`](tests/)

**Try it:**
```bash
uv run pytest
uv run python client/demo_client.py --mode memory
uv run python client/demo_client.py --mode stdio
```

**Checkpoint:** All tests pass; demo client creates a note and reads `note://{id}`.

---

## Wire it into Cursor

Copy the `knowledge-mcp` block from [`examples/cursor.mcp.json`](examples/cursor.mcp.json) into your Cursor MCP settings. Reload, then ask:

> Create a note titled "MCP practice" tagged mcp with priority high.

Cursor launches the server over stdio and calls `create_note` for you.

---

## Suggested exercises

1. Add an `update_note` tool that changes title/body/tags.
2. Add a resource `notes://tag/{tag}` that lists matching notes.
3. Add a prompt `explain_tag` that loads notes for one tag.
4. Restrict `import_url` to an allowlisted set of hosts.
5. Add a pytest that mocks `httpx` for `import_url`.
