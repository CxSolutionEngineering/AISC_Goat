"""Hosted-model SDK clients from multiple providers (demo, not functional)."""

import os

import anthropic
import cohere
import openai
from google import genai
from litellm import completion
from together import Together
from mistralai import Mistral

ANTHROPIC_MODEL = "claude-sonnet-4-5"
OPENAI_MODEL = "gpt-4o"
GEMINI_MODEL = "gemini-2.0-flash"
COHERE_MODEL = "command-r-plus"
TOGETHER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
MISTRAL_MODEL = "mistral-large-latest"


def ask_anthropic(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=ANTHROPIC_MODEL, max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def ask_openai(prompt: str) -> str:
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    r = client.chat.completions.create(
        model=OPENAI_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content


def ask_gemini(prompt: str) -> str:
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    return client.models.generate_content(model=GEMINI_MODEL, contents=prompt).text


def ask_cohere(prompt: str) -> str:
    client = cohere.ClientV2(api_key=os.environ["COHERE_API_KEY"])
    return client.chat(
        model=COHERE_MODEL, messages=[{"role": "user", "content": prompt}]
    ).message.content[0].text


def ask_together(prompt: str) -> str:
    client = Together(api_key=os.environ["TOGETHER_API_KEY"])
    r = client.chat.completions.create(
        model=TOGETHER_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content


def ask_mistral(prompt: str) -> str:
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    r = client.chat.complete(
        model=MISTRAL_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content


def ask_via_litellm(prompt: str, model: str = "openrouter/anthropic/claude-sonnet-4.5") -> str:
    """Gateway-style routing through LiteLLM / OpenRouter."""
    r = completion(model=model, messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content
