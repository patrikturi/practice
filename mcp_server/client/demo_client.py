"""Step 7: demo MCP client against knowledge-mcp (stdio subprocess or in-memory).

Usage:
  uv run python client/demo_client.py
  uv run python client/demo_client.py --http http://127.0.0.1:8000/mcp
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from mcp import Client
from mcp.client.stdio import StdioServerParameters


ROOT = Path(__file__).resolve().parents[1]


async def run_in_memory() -> None:
    """Connect directly to an in-process server (no transport)."""
    # Import after path setup so the installed package is used via uv run.
    from knowledge_mcp.db import NoteRepository
    from knowledge_mcp.server import create_server

    repo = NoteRepository(":memory:")
    server = create_server(repo)

    async with Client(server) as client:
        tools = await client.list_tools()
        print("Tools:", ", ".join(t.name for t in tools.tools))

        created = await client.call_tool(
            "create_note",
            {
                "note": {
                    "title": "Hello MCP",
                    "body": "Notes from the demo client.",
                    "tags": ["demo", "mcp"],
                    "priority": "high",
                }
            },
        )
        print("Created:", created.structured_content)

        listed = await client.call_tool("list_notes", {"limit": 5})
        print("Listed:", listed.structured_content)

        notes = (listed.structured_content or {}).get("notes") or []
        if notes:
            note_id = notes[0]["id"]
            resource = await client.read_resource(f"note://{note_id}")
            text = resource.contents[0].text if resource.contents else ""
            print("Resource preview:\n", text[:300])


async def run_stdio() -> None:
    """Launch the server as a stdio subprocess (how Cursor does it)."""
    params = StdioServerParameters(
        command="uv",
        args=["run", "--directory", str(ROOT), "python", "-m", "knowledge_mcp"],
        env={"KNOWLEDGE_MCP_DB": str(ROOT / "data" / "demo-client.db")},
    )
    async with Client(params) as client:
        pong = await client.call_tool("ping", {})
        print("Ping:", pong.structured_content or pong.content)
        tools = await client.list_tools()
        print("Tools:", ", ".join(t.name for t in tools.tools))


async def run_http(url: str) -> None:
    """Connect to a running Streamable HTTP server."""
    async with Client(url) as client:
        pong = await client.call_tool("ping", {})
        print("Ping:", pong.structured_content or pong.content)
        tools = await client.list_tools()
        print("Tools:", ", ".join(t.name for t in tools.tools))


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo client for knowledge-mcp.")
    parser.add_argument(
        "--mode",
        choices=("memory", "stdio", "http"),
        default="memory",
        help="Connection mode (default: in-memory).",
    )
    parser.add_argument(
        "--http",
        default="http://127.0.0.1:8000/mcp",
        help="URL when --mode http.",
    )
    args = parser.parse_args()

    if args.mode == "memory":
        asyncio.run(run_in_memory())
    elif args.mode == "stdio":
        asyncio.run(run_stdio())
    else:
        asyncio.run(run_http(args.http))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
