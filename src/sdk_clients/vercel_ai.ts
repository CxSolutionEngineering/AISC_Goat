// Vercel AI SDK + provider packages (demo only).
import { generateText } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { openai } from "@ai-sdk/openai";

export async function compare(prompt: string) {
  const [a, b] = await Promise.all([
    generateText({ model: anthropic("claude-sonnet-4-5"), prompt }),
    generateText({ model: openai("gpt-4o"), prompt }),
  ]);
  return { anthropic: a.text, openai: b.text };
}
