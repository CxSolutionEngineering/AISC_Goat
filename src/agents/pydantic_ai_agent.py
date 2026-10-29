"""Pydantic AI typed agent targeting Anthropic."""

from pydantic import BaseModel
from pydantic_ai import Agent


class Verdict(BaseModel):
    safe: bool
    reason: str


reviewer = Agent("anthropic:claude-sonnet-4-5", output_type=Verdict,
                 system_prompt="Review the dependency for supply chain risk.")
