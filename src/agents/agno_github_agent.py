"""Agno agent wired to the GitHub MCP server (adapted from awesome-llm-apps)."""

import asyncio
import os
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters


async def run(query: str) -> str:
    params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_TOKEN", "")},
    )
    async with MCPTools(server_params=params) as mcp_tools:
        agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            tools=[mcp_tools],
            instructions=dedent("Answer questions about GitHub repositories."),
        )
        return (await agent.arun(query)).content


if __name__ == "__main__":
    print(asyncio.run(run("Summarize open PRs in acme/widgets")))
