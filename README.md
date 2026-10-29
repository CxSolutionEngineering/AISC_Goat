# AI Supply Chain Goat (AISC_Goat)

**Repo:** https://github.com/CxSolutionEngineering/AISC_Goat

AI Supply Chain Goat is an intentionally vulnerable AI codebase for validating
and demoing Checkmarx AI Supply Chain Security. It is the single demo project
referenced by the AI Supply Chain Security demo narrative. It does two jobs:

1. **Live scan validation (branch 00, dortucx).** It loads **real, public,
   scannable** Hugging Face models from the `dortucx` account. Unlike the
   synthetic `01`–`07` scenarios (which use fictional `GoatModel` names), this
   branch references actual HF repo IDs so the full pipeline can be validated
   end to end.
2. **AI supply chain discovery demo.** It carries a spread of AI components from
   several providers (models, SDKs, agent frameworks, MCP clients and servers,
   and agent skills) so the Global Inventory has realistic, varied entries.

> Code is illustrative. Apart from the original `src/` entrypoints, nothing here
> is expected to run end to end. It exists to be scanned, not executed.

## Using it in a demo

```bash
git clone https://github.com/CxSolutionEngineering/AISC_Goat.git
```

Onboard the repo as a project in a Checkmarx One tenant with AI Supply Chain
Security enabled and run a full scan. Before a customer call, confirm that
`dortucx/unkindmodel` and `TinyLlama 1.1B Chat v1.0` show Risk Evaluation
findings (see [Expected scan results](#expected-scan-results)).

## Scan pipeline

```
Pedro discovery (regex over this repo)
  -> emits AI assets (models, SDKs, agents, MCP servers, skills)
    -> ai-sc-risks filters to AI Model, passes HF URL
      -> LLM Scanner clones e.g. https://huggingface.co/dortucx/unkindmodel (anonymous, ungated)
        -> finds risks in the model repo -> written to scan_risks
```

## Repository layout

```
.
├── .mcp.json                  # Project MCP server config (committed on purpose)
├── .gitignore
├── package.json               # npm AI dependencies (JS/TS side)
├── requirements.txt           # PyPI AI dependencies
├── src/
│   ├── model_loader.py        # Original: dortucx model + tokenizer loaders
│   ├── inference_service.py   # Original: pipeline entrypoint
│   ├── models/hub_models.py   # Multi-provider HF Hub models
│   ├── sdk_clients/           # Hosted model SDKs (Python + Vercel AI SDK in TS)
│   └── agents/                # Agent frameworks, MCP-using agents, RAG pipeline
├── mcp/
│   ├── servers/               # Custom MCP servers (Python FastMCP, TypeScript SDK)
│   └── clients/               # Python MCP client (stdio + streamable HTTP)
├── skills/                    # Agent skills (SKILL.md format) + registry.json
└── agents/upstream/           # Agent apps copied from awesome-llm-apps
```

## Expected scan results

| Model | Expected findings | Notes |
|---|---|---|
| `dortucx/unkindmodel` | 11 High: 4 Malicious pickle / Torch gadget patterns, 2 Auto-loading from JSON / config, 5 Direct OS command execution | Known-malicious fixture. `config.json` uses `auto_map` to load `this_tokenizer_is_evil_actually.py`, which calls `os.system`. |
| `dortucx/unkindtokenizer` | Findings expected | Known-malicious fixture. |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 4 High: Malicious pickle / Torch gadget patterns (e.g. `eval` in `tokenizer.model`) | Mainstream model. `tokenizer.model` is a SentencePiece vocabulary, so the `eval` hit may be a literal token rather than code. Treat as "flagged for review." |
| `google/gemma-2-2b-it` | Skipped (`no credentials configured`) | Gated model; exercises the skip path. |
| Other models | None expected | Mainstream models included for inventory breadth. |

The `dortucx` fixtures back the LLM Scanner's own
`tests/integration/hf/unkindmodel.json` / `unkindtokenizer.json`, so a working
scan should return findings rather than an empty result. Counts reflect the
scanner at the time of writing and may shift as rules are tuned.

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

Mistral and Gemma are referenced only through constants (`MISTRAL_REPO`,
`GEMMA_REPO`), which tests whether discovery resolves IDs that aren't passed
inline.

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

**About `.mcp.json`:** this is the project-scoped MCP config read by Claude Code
and other MCP clients, and it is committed on purpose. Playwright and Notion are
declared **only** here, so if they appear in the inventory, config-file
discovery is working; if only code-referenced servers appear, that is a coverage
gap. The file contains no secrets; tokens are `${ENV_VAR}` placeholders.

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
| `supply-chain-reviewer` | Local | No |

`skills/registry.json` lists all four with their source and `npx skills add`
install commands.

### Upstream agent apps (`agents/upstream/`)

`github_mcp_agent`, `multi_mcp_agent_router`, `mixture_of_agents`, and
`rag_agent_cohere`, copied unmodified with their own `requirements.txt` files.
Those pins intentionally differ from (and in places conflict with) the root
`requirements.txt`, which gives SCA something to reconcile.

## Intentional risk patterns

| Pattern | Where |
|---|---|
| `trust_remote_code=True` | `src/model_loader.py`, `src/inference_service.py`, `src/models/hub_models.py` (phi-2) |
| Known-malicious model artifacts | `dortucx/unkindmodel`, `dortucx/unkindtokenizer` |
| Gated model (credential skip path) | `google/gemma-2-2b-it` |
| Direct file pull bypassing `from_pretrained` | `hf_hub_download` in `src/models/hub_models.py` |
| Unpinned MCP package (`@latest`) | `.mcp.json` (Playwright) |
| Over-privileged MCP tool (`shell=True`) | `run_shell` in `mcp/servers/notes_server.py` |
| Remote MCP servers (third-party data egress) | Context7, DeepWiki |
| Floating dependency ranges | `requirements.txt`, `package.json` |
| Conflicting nested manifests | `agents/upstream/*/requirements.txt` |
| Skills that ship executable scripts | `skills/dependency-doctor`, `skills/commit-archaeologist`, `skills/first-reader` |

## Environment variables

Nothing in the repo holds real credentials. If you do run anything, these are
read from the environment (put them in a local `.env`, which is git-ignored):

`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `COHERE_API_KEY`,
`TOGETHER_API_KEY`, `MISTRAL_API_KEY`, `GITHUB_TOKEN`, `NOTION_TOKEN`, and
optionally `HF_TOKEN` for the gated Gemma model.

## Run locally (optional)

Only the original entrypoint is meant to run, and it loads a malicious fixture
with `trust_remote_code=True`. **Run it only in a disposable sandbox.**

```bash
pip install -r requirements.txt
python -m src.inference_service
```

## Attribution

Skills under `skills/` (except `supply-chain-reviewer`) and everything under
`agents/upstream/` are copied from
[Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)
under the Apache-2.0 license. See `agents/upstream/LICENSE-awesome-llm-apps`.
