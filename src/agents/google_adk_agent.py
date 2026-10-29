"""Google ADK agent calling a remote MCP toolset."""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

root_agent = LlmAgent(
    name="adk_docs_agent",
    model="gemini-2.0-flash",
    instruction="Use the docs tools to answer developer questions.",
    tools=[
        MCPToolset(
            connection_params=SseServerParams(url="https://mcp.deepwiki.com/sse")
        )
    ],
)
