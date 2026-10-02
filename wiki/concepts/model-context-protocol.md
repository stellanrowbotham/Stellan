---
type: concept
title: Model Context Protocol (MCP)
aliases: ["MCP", "MCP server"]
tags: [llm, agents, protocol]
created: 2026-10-02
updated: 2026-10-02
sources: [src-karpathy-llm-wiki, src-qmd-readme]
---

# Model Context Protocol (MCP)
A protocol that lets an LLM agent call external tools natively, instead of shelling out to a CLI.

## Explanation
In the [[llm-wiki]] setup, an agent can reach a tool in two ways: run its CLI and parse the output, or connect to its **MCP server** and call it as a native tool ([[src-karpathy-llm-wiki]]). [[qmd]] supports both. Its MCP server exposes `query`, `get`, `multi_get`, and `status`. It runs over stdio (one subprocess per client) or HTTP (a shared, long-lived server on `localhost:8181` that keeps models loaded) ([[src-qmd-readme]]).

qmd's README says the CLI alone "works perfectly fine"; MCP is for "tighter integration" ([[src-qmd-readme]]).

## Evidence & claims
- qmd's MCP tools silently ignore unknown parameters. For example, a singular `collection` is ignored, and only the array `collections` works. ([[src-qmd-readme]])
- MCP over HTTP needs DNS-rebinding protection. qmd rejects non-loopback `Origin` headers. ([[src-qmd-readme]])
- *(general knowledge, unverified here)* Anthropic introduced MCP as an open standard in late 2024.

## Tensions & contradictions
- None yet.

## Related
- [[qmd]]
- [[llm-wiki]]
