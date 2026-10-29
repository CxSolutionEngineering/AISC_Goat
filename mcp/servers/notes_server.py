"""A small custom MCP server (FastMCP) exposing tools, a resource and a prompt."""

import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes-server")


@mcp.tool()
def add_note(title: str, body: str) -> str:
    """Store a note."""
    return f"saved {title}"


@mcp.tool()
def run_shell(cmd: str) -> str:
    """Run a shell command (intentionally over-privileged for the demo)."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


@mcp.resource("notes://{title}")
def get_note(title: str) -> str:
    return f"contents of {title}"


@mcp.prompt()
def summarize(title: str) -> str:
    return f"Summarize the note titled {title}."


if __name__ == "__main__":
    mcp.run(transport="stdio")
