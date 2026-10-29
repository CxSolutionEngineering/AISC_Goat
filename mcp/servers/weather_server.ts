// Node/TypeScript MCP server using the official SDK (demo only).
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "weather", version: "0.0.1" });

server.tool("get_forecast", { city: z.string() }, async ({ city }) => ({
  content: [{ type: "text", text: `Forecast for ${city}: sunny` }],
}));

await server.connect(new StdioServerTransport());
