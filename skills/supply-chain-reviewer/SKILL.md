---
name: supply-chain-reviewer
description: Reviews a repository's AI dependencies (models, MCP servers, skills, SDKs) and flags unpinned or untrusted ones. Use when asked to audit AI supply chain risk.
license: Apache-2.0
metadata:
  author: goat-demo
  version: 0.0.1
---

# Supply Chain Reviewer

1. List models referenced via `from_pretrained`, `snapshot_download`, `hf_hub_download`.
2. List MCP servers from `.mcp.json` and `mcp/clients/`.
3. List skills under `skills/` and flag any with executable `scripts/`.
4. Report anything unpinned (`@latest`, floating tags, no revision hash).
