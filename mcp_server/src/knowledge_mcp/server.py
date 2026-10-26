"""Knowledge-base MCP server entrypoint."""

from __future__ import annotations

import argparse

from mcp.server import MCPServer

from knowledge_mcp.db import NoteRepository, default_db_path
from knowledge_mcp.prompts import register_prompts
from knowledge_mcp.resources import register_resources
from knowledge_mcp.tools import register_tools


def create_server(repo: NoteRepository | None = None) -> MCPServer:
    """Build a fully wired knowledge-mcp server."""
    repository = repo or NoteRepository()
    mcp = MCPServer(
        "knowledge-mcp",
        instructions=(
            "Personal knowledge-base MCP server. "
            "Use tools to create/search/delete notes, resources to read note:// URIs, "
            "and prompts for summarize_note / weekly_review workflows."
        ),
    )
    register_tools(mcp, repository)
    register_resources(mcp, repository)
    register_prompts(mcp, repository)
    return mcp


# Module-level server for `mcp dev` / `mcp run` which import this attribute.
mcp = create_server()


def main(argv: list[str] | None = None) -> None:
    """CLI: stdio (default) or Streamable HTTP."""
    parser = argparse.ArgumentParser(description="Run the knowledge-mcp MCP server.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help="stdio for Cursor; streamable-http for a local HTTP endpoint.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP bind host.")
    parser.add_argument("--port", type=int, default=8000, help="HTTP bind port.")
    args = parser.parse_args(argv)

    # Recreate so KNOWLEDGE_MCP_DB changes are picked up at process start.
    server = create_server(NoteRepository(default_db_path()))

    if args.transport == "stdio":
        server.run(transport="stdio")
    else:
        server.run(transport="streamable-http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
