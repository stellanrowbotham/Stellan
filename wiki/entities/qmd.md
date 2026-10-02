---
type: entity
kind: tool
title: qmd
aliases: ["QMD", "Query Markup Documents", "@tobilu/qmd"]
tags: [tool, search, markdown, mcp]
created: 2026-10-01
updated: 2026-10-02
sources: [src-karpathy-llm-wiki, src-qmd-readme]
---

# qmd
A local, on-device [[hybrid-search]] engine for markdown. It is the tool suggested for when an [[llm-wiki]] outgrows its index file.

## Summary
qmd ("Query Markup Documents") indexes folders of markdown, such as notes, transcripts, docs, and wikis, into one SQLite file. It runs BM25 keyword search, vector search, LLM query expansion, and LLM re-ranking, all locally on GGUF models via node-llama-cpp ([[src-qmd-readme]]). [[andrej-karpathy]] recommends it as the search layer for an LLM wiki because it has both a CLI and an [[model-context-protocol|MCP]] server ([[src-karpathy-llm-wiki]]).

## Key facts
- **Three modes:** `search` (BM25), `vsearch` (vector), and `query` (hybrid with expansion and rerank, the best quality). ([[src-qmd-readme]])
- **Fusion:** [[reciprocal-rank-fusion]] with k=60, ×2 weight for the original query, a bonus for top-ranked results, then a rerank blended by rank position. ([[src-qmd-readme]])
- **Models:** about 2 GB in total across three GGUF models: embeddinggemma-300M, qwen3-reranker-0.6b, and a fine-tuned query-expansion-1.7B model. ([[src-qmd-readme]])
- **[[document-chunking|Chunking]]:** ~900 tokens with 15% overlap, cut at markdown-aware break points. ([[src-qmd-readme]])
- **Context tree:** descriptions attached to paths are returned with results. The README calls this "the key feature." ([[src-qmd-readme]])
- **Agent interfaces:** CLI with `--json`/`--files`, MCP tools `query`/`get`/`multi_get`/`status`, an HTTP server at `localhost:8181`, and a Node/Bun SDK. ([[src-qmd-readme]])
- **Claude Code:** `claude plugin marketplace add tobi/qmd` followed by `claude plugin install qmd@qmd`. ([[src-qmd-readme]])
- **Install:** `npm install -g @tobilu/qmd`. Requires Node ≥ 22 or Bun ≥ 1.0. ([[src-qmd-readme]])
- **License:** MIT. Repo: `github.com/tobi/qmd`. ([[src-qmd-readme]])
- *(general knowledge, unverified here)* The GitHub user `tobi` is widely understood to be Tobi Lütke, CEO of Shopify.

## Tensions & contradictions
- ⚠️ **Expansion count:** the README's diagrams show 2 LLM variants, but its Fusion Strategy text says 1. Status: open. The code (`src/llm.ts`) would settle it. ([[src-qmd-readme]])
- ⚠️ **Rerank pool:** "Top 30" in the diagram and text, but `candidateLimit` defaults to 40. *(synthesis)* A likely reading is that 40 is the configurable cap and 30 is outdated documentation. Status: open. ([[src-qmd-readme]])
- ⚠️ *(minor)* The `multi_get` max-bytes default is 10 KB for MCP but 64 KB for the CLI and SDK. ([[src-qmd-readme]])

## Connections
- [[hybrid-search]], [[reciprocal-rank-fusion]], [[document-chunking]]: the techniques it implements
- [[retrieval-augmented-generation]]: qmd is retrieval, but pointed at compiled wiki pages rather than raw chunks
- [[model-context-protocol]]: how agents call it as a native tool
- [[obsidian]]: complementary. Obsidian is for humans browsing; qmd is for agents searching.
- [[qmd-setup-for-this-wiki]]: the plan for adopting it here

## Status in this wiki
- Not installed. This wiki uses `tools/wiki.py search`, a naive BM25 script, until about 100 sources. See [[qmd-setup-for-this-wiki]]. *(synthesis)*
