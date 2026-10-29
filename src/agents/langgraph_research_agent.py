"""LangGraph ReAct agent mixing Anthropic + OpenAI models and web search tools."""

from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

planner = ChatAnthropic(model="claude-sonnet-4-5")
summarizer = ChatOpenAI(model="gpt-4o-mini")

research_agent = create_react_agent(planner, tools=[DuckDuckGoSearchRun()])
summary_agent = create_react_agent(summarizer, tools=[])


def research(topic: str) -> str:
    raw = research_agent.invoke({"messages": [("user", f"Research: {topic}")]})
    cond = summary_agent.invoke({"messages": [("user", raw["messages"][-1].content)]})
    return cond["messages"][-1].content
