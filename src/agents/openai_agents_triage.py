"""OpenAI Agents SDK triage agent with handoffs and a function tool."""

from agents import Agent, Runner, function_tool


@function_tool
def lookup_order(order_id: str) -> str:
    return f"Order {order_id}: shipped"


billing = Agent(name="Billing", instructions="Handle billing questions.")
support = Agent(name="Support", instructions="Handle support.", tools=[lookup_order])
triage = Agent(
    name="Triage",
    instructions="Route the user to the right specialist.",
    handoffs=[billing, support],
    model="gpt-4o",
)


async def handle(msg: str) -> str:
    return (await Runner.run(triage, msg)).final_output
