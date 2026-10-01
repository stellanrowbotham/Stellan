---
type: entity
kind: tool
title: qmd
aliases: []
tags: [tool, search, markdown]
created: 2026-10-01
updated: 2026-10-01
sources: [src-karpathy-llm-wiki]
---

# qmd
Local, on-device search engine for markdown files. Suggested for when an [[llm-wiki]] outgrows its index file.

## Summary
qmd offers hybrid BM25/vector search with LLM re-ranking, all running on-device. It has a CLI the agent can shell out to and an MCP server the agent can use as a native tool ([[src-karpathy-llm-wiki]]).

## Key facts
- Hybrid BM25 + vector search, with LLM re-ranking. ([[src-karpathy-llm-wiki]])
- Has both a CLI and an MCP server. ([[src-karpathy-llm-wiki]])
- Optional: at small scale the `index.md` file is enough. A home-made naive search script is another option. ([[src-karpathy-llm-wiki]])

## Connections
- [[llm-wiki]]: optional tooling layer
- [[retrieval-augmented-generation]]: qmd is retrieval, but over compiled wiki pages
- [[obsidian]]: complementary browsing tool

## Status in this wiki
- Not installed. Revisit when the wiki reaches about 100 sources or the index gets hard to scan. *(synthesis)*
