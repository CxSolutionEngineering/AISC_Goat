# AI Supply Chain Goat (AISC_Goat)

An intentionally vulnerable codebase for testing AI supply chain security
tooling. It pulls in a broad, realistic mix of AI components (open-weight
models, hosted model SDKs, agent frameworks, MCP clients and servers, and agent
skills) and seeds them with common AI supply chain risks, so you can see what
your discovery and scanning tools actually find.

> [!WARNING]
> **Do not run this code outside a disposable sandbox.** It references public
> Hugging Face models that contain malicious payloads and loads them with
> `trust_remote_code=True`. Most of the code is illustrative and is meant to be
> scanned, not executed.

## Why this exists

AI components rarely show up in a traditional SBOM or SCA report. Models are
pulled by string ID at runtime, MCP servers are declared in config files and
launched with `npx` or `uvx`, and agent skills ship their own executable
scripts. AISC_Goat gives you a single repository to check whether a tool can:

- **Discover** AI assets across Python, TypeScript, JSON config, and Markdown
  skill definitions.
- **Attribute** each asset to the exact file and line where it is referenced.
- **Detect risk** in the model artifacts themselves, not just in the code that
  loads them.
- **Produce an AI bill of materials (AI-BOM)** that reflects what is really in
  the codebase.

## Quick start

```bash
git clone https://github.com/CxSolutionEngineering/AISC_Goat.git
```

Point your AI supply chain, SCA, or SAST tooling at the repository and compare
its results with the inventory and risk tables below.

## Repository layout

```
.
├── .mcp.json                  # Project MCP server config (committed on purpose)
├── .gitignore
├── package.json               # npm AI dependencies (JS/TS side)
├── requirements.txt           # PyPI AI dependencies
├── src/
│   ├── model_loader.py        # Loads the malicious test model + tokenizer
│   ├── inference_service.py   # Pipeline entrypoint
│   ├── models/hub_models.py   # Multi-provider Hugging Face Hub models
│   ├── sdk_clients/           # Hosted model SDKs (Python + Vercel AI SDK in TS)
│   └── agents/                # Agent frameworks, MCP-using agents, RAG pipeline
├── mcp/
│   ├── servers/               # Custom MCP servers (Python FastMCP, TypeScript SDK)
│   └── clients/               # Python MCP client (stdio + streamable HTTP)
├── skills/                    # Agent skills (SKILL.md format) + registry.json
└── agents/upstream/           # Agent apps copied from awesome-llm-apps
```

## What a scanner should find

### Model artifact risks

| Model | What's in it | Why it matters |
|---|---|---|
| `dortucx/unkindmodel` | `config.json` uses `auto_map` to point `AutoModel` at a bundled Python file, which calls `os.system`. Binary files also contain pickle / Torch gadget patterns. | Loading the model with `trust_remote_code=True` runs attacker code with the privileges of the process: a developer laptop, a CI runner, or an inference server and its credentials. |
| `dortucx/unkindtokenizer` | Malicious test tokenizer. | Tokenizers are loaded automatically alongside models and are easy to overlook. |
| `google/gemma-2-2b-it` | Gated model; requires an access token. | Checks how a tool handles models it cannot download anonymously. |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | A widely used, mainstream model. | Not known to be malicious. Heuristic scanners may flag byte patterns in its binary files (for example, the string `eval` inside the SentencePiece vocabulary), which makes it a useful false-positive and triage check. |
| Other models | Mainstream models from major providers. | Included for inventory breadth. No risks expected. |

The `dortucx` models are public test fixtures built to be malicious. They are
not affiliated with this repository.

### Code and configuration risks

| Pattern | Where |
|---|---|
| `trust_remote_code=True` | `src/model_loader.py`, `src/inference_service.py`, `src/models/hub_models.py` (phi-2) |
| Direct file pull bypassing `from_pretrained` | `hf_hub_download` in `src/models/hub_models.py` |
| Model IDs referenced only through constants | `MISTRAL_REPO`, `GEMMA_REPO` in `src/models/hub_models.py` |
| Unpinned MCP package (`@latest`) | `.mcp.json` (Playwright) |
| Over-privileged MCP tool (`shell=True`) | `run_shell` in `mcp/servers/notes_server.py` |
| Remote MCP servers (third-party data egress) | Context7, DeepWiki |
| MCP servers declared only in config | Playwright and Notion in `.mcp.json` |
| Floating dependency ranges | `requirements.txt`, `package.json` |
| Conflicting nested manifests | `agents/upstream/*/requirements.txt` |
| Agent skills that ship executable scripts | `skills/dependency-doctor`, `skills/commit-archaeologist`, `skills/first-reader` |

## Component inventory

### Models (Hugging Face Hub)

| Repo ID | Provider | Referenced in | Load pattern |
|---|---|---|---|
| `dortucx/unkindmodel` | dortucx (test fixture) | `src/model_loader.py`, `src/inference_service.py` | `from_pretrained` with `trust_remote_code=True`, `snapshot_download` |
| `dortucx/unkindtokenizer` | dortucx (test fixture) | `src/model_loader.py`, `src/inference_service.py` | `AutoTokenizer.from_pretrained` |
| `Qwen/Qwen2.5-0.5B-Instruct` | Alibaba | `src/models/hub_models.py` | `from_pretrained` (literal) |
| `mistralai/Mistral-7B-Instruct-v0.2` | Mistral AI | `src/models/hub_models.py` | `from_pretrained` via module constant |
| `microsoft/phi-2` | Microsoft | `src/models/hub_models.py` | `from_pretrained` with `trust_remote_code=True`; `hf_hub_download` |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` | DeepSeek | `src/models/hub_models.py` | `pipeline(model=...)` |
| `google/gemma-2-2b-it` | Google (gated) | `src/models/hub_models.py` | `from_pretrained` via module constant |
| `BAAI/bge-small-en-v1.5` | BAAI | `src/models/hub_models.py` | `SentenceTransformer` |
| `sentence-transformers/all-MiniLM-L6-v2` | SBERT | `src/models/hub_models.py`, `src/agents/rag_pipeline.py` | `SentenceTransformer`, `HuggingFaceEmbeddings` |
| `openai/whisper-tiny` | OpenAI | `src/models/hub_models.py` | `AutoProcessor` / `AutoModelForSpeechSeq2Seq` |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | TinyLlama | `src/models/hub_models.py` | `snapshot_download` |

### Hosted model SDKs

| Provider | Package | Model | File |
|---|---|---|---|
| Anthropic | `anthropic` | `claude-sonnet-4-5` | `src/sdk_clients/providers.py` |
| OpenAI | `openai` | `gpt-4o` | `src/sdk_clients/providers.py` |
| Google | `google-genai` | `gemini-2.0-flash` | `src/sdk_clients/providers.py` |
| Cohere | `cohere` | `command-r-plus`, `rerank-english-v3.0` | `src/sdk_clients/providers.py`, `src/agents/rag_pipeline.py` |
| Together | `together` | `meta-llama/Llama-3.3-70B-Instruct-Turbo` | `src/sdk_clients/providers.py` |
| Mistral | `mistralai` | `mistral-large-latest` | `src/sdk_clients/providers.py` |
| LiteLLM / OpenRouter | `litellm` | `openrouter/anthropic/claude-sonnet-4.5` | `src/sdk_clients/providers.py` |
| Vercel AI SDK | `ai`, `@ai-sdk/anthropic`, `@ai-sdk/openai` | `claude-sonnet-4-5`, `gpt-4o` | `src/sdk_clients/vercel_ai.ts` |
| Ollama (local) | `ollama` | `llama3.1:8b` | `src/agents/rag_pipeline.py` |

### Agent frameworks

| Framework | File | What it shows |
|---|---|---|
| Agno | `src/agents/agno_github_agent.py` | Agent with GitHub MCP server via `MCPTools` |
| LangGraph | `src/agents/langgraph_research_agent.py` | ReAct agents mixing Anthropic and OpenAI models, web search tool |
| OpenAI Agents SDK | `src/agents/openai_agents_triage.py` | Triage agent with handoffs and a function tool |
| Google ADK | `src/agents/google_adk_agent.py` | `LlmAgent` with a remote MCP toolset (DeepWiki SSE) |
| Pydantic AI | `src/agents/pydantic_ai_agent.py` | Typed-output agent on Anthropic |
| LangChain RAG | `src/agents/rag_pipeline.py` | HF embeddings, Qdrant, Cohere rerank, Ollama |

### MCP servers

| Server | Declared in | Transport | Pinned? |
|---|---|---|---|
| `@modelcontextprotocol/server-github` | `.mcp.json`, `src/agents/agno_github_agent.py`, upstream agents | stdio (npx) | No |
| `@modelcontextprotocol/server-filesystem` | `.mcp.json`, `mcp/clients/multi_client.py` | stdio (npx) | No |
| `@playwright/mcp@latest` | `.mcp.json` only | stdio (npx) | No (`@latest`) |
| `@notionhq/notion-mcp-server` | `.mcp.json` only | stdio (npx) | No |
| `mcp-server-fetch` | `.mcp.json`, `mcp/clients/multi_client.py` | stdio (uvx) | No |
| `notes-server` (custom) | `mcp/servers/notes_server.py`, `.mcp.json` | stdio (Python FastMCP) | Local |
| `weather` (custom) | `mcp/servers/weather_server.ts` | stdio (TypeScript SDK) | Local |
| Context7 | `.mcp.json`, `mcp/clients/multi_client.py` | Remote HTTP | n/a |
| DeepWiki | `.mcp.json`, `mcp/clients/multi_client.py`, `src/agents/google_adk_agent.py` | Remote SSE / HTTP | n/a |

`.mcp.json` is the project-scoped MCP configuration format read by Claude Code
and other MCP clients, and it is committed on purpose. Playwright and Notion are
declared **only** there, so they are a direct test of whether a tool discovers
MCP servers from configuration as well as from code. The file contains no
secrets; tokens are `${ENV_VAR}` placeholders.

### MCP clients

| Client | File |
|---|---|
| Python `mcp` `ClientSession` (stdio + streamable HTTP) | `mcp/clients/multi_client.py` |
| Agno `MCPTools` | `src/agents/agno_github_agent.py`, `agents/upstream/github_mcp_agent/` |
| Google ADK `MCPToolset` | `src/agents/google_adk_agent.py` |
| Raw `StdioServerParameters` router | `agents/upstream/multi_mcp_agent_router/agent_forge.py` |

### Agent skills

| Skill | Source | Ships scripts? |
|---|---|---|
| `dependency-doctor` | awesome-llm-apps | Yes (`scripts/dep_doctor.py`) |
| `commit-archaeologist` | awesome-llm-apps | Yes (`scripts/archaeologist.py`) |
| `first-reader` | awesome-llm-apps | Yes (several Python scripts + HTML template) |
| `supply-chain-reviewer` | This repo | No |

`skills/registry.json` lists all four with their source and `npx skills add`
install commands.

### Upstream agent apps (`agents/upstream/`)

`github_mcp_agent`, `multi_mcp_agent_router`, `mixture_of_agents`, and
`rag_agent_cohere`, copied unmodified with their own `requirements.txt` files.
Their pins intentionally differ from (and in places conflict with) the root
`requirements.txt`.

## Environment variables

The repository contains no real credentials. If you run anything, these are
read from the environment (use a local `.env`, which is git-ignored):

`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `COHERE_API_KEY`,
`TOGETHER_API_KEY`, `MISTRAL_API_KEY`, `GITHUB_TOKEN`, `NOTION_TOKEN`, and
optionally `HF_TOKEN` for the gated Gemma model.

## Running it (sandbox only)

Only the `src/` entrypoint is meant to run, and it loads a malicious test model
with `trust_remote_code=True`. Use a throwaway VM or container with no
credentials and no access to anything you care about.

```bash
pip install -r requirements.txt
python -m src.inference_service
```

## Contributing

Additions are welcome, especially new AI component types, providers, or risk
patterns that tools commonly miss. Please keep the repo safe to clone: reference
malicious artifacts by public ID rather than committing them, and never commit
real credentials.

## Attribution

Skills under `skills/` (except `supply-chain-reviewer`) and everything under
`agents/upstream/` are copied from
[Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)
under the Apache-2.0 license. See `agents/upstream/LICENSE-awesome-llm-apps`.

Model names and trademarks belong to their respective owners. Their inclusion
here does not imply that any mainstream model is unsafe.
