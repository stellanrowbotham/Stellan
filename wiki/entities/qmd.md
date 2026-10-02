---
type: entity
kind: tool
title: qmd
aliases: ["QMD", "Query Markup Documents", "@tobilu/qmd"]
tags: [tool, search, markdown, mcp]
created: 2026-10-01
updated: 2026-10-02
sources: [src-karpathy-llm-wiki, src-qmd-readme, src-qmd-source-code]
---

# qmd
A local, on-device [[hybrid-search]] engine for markdown. It is the tool suggested for when an [[llm-wiki]] outgrows its index file.

## Summary
qmd ("Query Markup Documents") indexes folders of markdown, such as notes, transcripts, docs, and wikis, into one SQLite file. It runs BM25 keyword search, vector search, LLM query expansion, and LLM re-ranking, all locally on GGUF models via node-llama-cpp ([[src-qmd-readme]]). [[andrej-karpathy]] recommends it as the search layer for an LLM wiki because it has both a CLI and an [[model-context-protocol|MCP]] server ([[src-karpathy-llm-wiki]]).

## Key facts
- **Three modes:** `search` (BM25), `vsearch` (vector), and `query` (hybrid with expansion and rerank, the best quality). ([[src-qmd-readme]])
- **Fusion:** [[reciprocal-rank-fusion]] with k=60, ×2 weight for the original query, a bonus for top-ranked results, then a rerank blended by rank position. ([[src-qmd-readme]]) The 2.0/1.0 weights are confirmed in code. ([[src-qmd-source-code]])
- **Strong-signal shortcut** (not in the README): if the BM25 probe's top hit scores ≥ 0.85 and leads the runner-up by ≥ 0.15, LLM expansion is skipped. Passing `--intent` disables the shortcut. ([[src-qmd-source-code]])
- **Rerank pool:** 40 candidates by default (`RERANK_CANDIDATE_LIMIT`). The best chunk of each document is reranked, not the whole body. ([[src-qmd-source-code]])
- **Models:** about 2 GB in total across three GGUF models: embeddinggemma-300M, qwen3-reranker-0.6b, and a fine-tuned query-expansion-1.7B model. ([[src-qmd-readme]])
- **[[document-chunking|Chunking]]:** ~900 tokens with 15% overlap, cut at markdown-aware break points. ([[src-qmd-readme]])
- **Context tree:** descriptions attached to paths are returned with results. The README calls this "the key feature." ([[src-qmd-readme]])
- **Agent interfaces:** CLI with `--json`/`--files`, MCP tools `query`/`get`/`multi_get`/`status`, an HTTP server at `localhost:8181`, and a Node/Bun SDK. ([[src-qmd-readme]])
- **Claude Code:** `claude plugin marketplace add tobi/qmd` followed by `claude plugin install qmd@qmd`. ([[src-qmd-readme]])
- **Install:** `npm install -g @tobilu/qmd`. Requires Node ≥ 22 or Bun ≥ 1.0. ([[src-qmd-readme]])
- **License:** MIT. Repo: `github.com/tobi/qmd`. ([[src-qmd-readme]])
- *(general knowledge, unverified here)* The GitHub user `tobi` is widely understood to be Tobi Lütke, CEO of Shopify.

## Tensions & contradictions
- ✅ **Expansion count:** the README's diagrams show 2 LLM variants, but its Fusion Strategy text says 1 ([[src-qmd-readme]]). **Resolved 2026-10-02:** neither is right. The model emits a *variable* number of typed `lex`/`vec`/`hyde` lines, filtered to those containing a query term, and expansion may be skipped entirely by the strong-signal shortcut ([[src-qmd-source-code]]).
- ✅ **Rerank pool:** the README says "Top 30" but `candidateLimit` defaults to 40 ([[src-qmd-readme]]). **Resolved:** the code uses 40. "Top 30" is stale documentation ([[src-qmd-source-code]]).
- ✅ *(minor)* **`multi_get` max bytes:** the README's MCP table says 10 KB, against 64 KB for the CLI and SDK ([[src-qmd-readme]]). **Resolved:** MCP also defaults to 64 KB in code ([[src-qmd-source-code]]).

## Connections
- [[hybrid-search]], [[reciprocal-rank-fusion]], [[document-chunking]]: the techniques it implements
- [[retrieval-augmented-generation]]: qmd is retrieval, but pointed at compiled wiki pages rather than raw chunks
- [[model-context-protocol]]: how agents call it as a native tool
- [[obsidian]]: complementary. Obsidian is for humans browsing; qmd is for agents searching.
- [[qmd-setup-for-this-wiki]]: the plan for adopting it here
- [[src-qmd-source-code]]: primary-source check of the README (commit 04e4dbd)

## Status in this wiki
- Not installed. This wiki uses `tools/wiki.py search`, a naive BM25 script, until about 100 sources. See [[qmd-setup-for-this-wiki]]. *(synthesis)*
