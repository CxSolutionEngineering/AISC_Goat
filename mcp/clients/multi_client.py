"""MCP client that connects to stdio and remote (streamable HTTP) servers."""

import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

STDIO_SERVERS = {
    "filesystem": StdioServerParameters(
        command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]),
    "fetch": StdioServerParameters(command="uvx", args=["mcp-server-fetch"]),
    "notes": StdioServerParameters(command="python", args=["mcp/servers/notes_server.py"]),
}
REMOTE_SERVERS = {
    "context7": "https://mcp.context7.com/mcp",
    "deepwiki": "https://mcp.deepwiki.com/mcp",
}


async def main() -> None:
    async with AsyncExitStack() as stack:
        sessions = {}
        for name, params in STDIO_SERVERS.items():
            r, w = await stack.enter_async_context(stdio_client(params))
            s = await stack.enter_async_context(ClientSession(r, w))
            await s.initialize()
            sessions[name] = s
        for name, url in REMOTE_SERVERS.items():
            r, w, _ = await stack.enter_async_context(streamablehttp_client(url))
            s = await stack.enter_async_context(ClientSession(r, w))
            await s.initialize()
            sessions[name] = s
        for n, s in sessions.items():
            print(n, [t.name for t in (await s.list_tools()).tools])


if __name__ == "__main__":
    asyncio.run(main())
