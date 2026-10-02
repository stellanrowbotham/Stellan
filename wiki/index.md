---
type: meta
title: Index
tags: [meta]
created: 2026-10-01
updated: 2026-10-02
---

# Index
Catalog of every page in the wiki. The agent reads this first on every query and updates it on every operation.

**Totals:** 3 sources · 4 entities · 8 concepts · 1 analysis · last updated 2026-10-02

## Overview
- [[overview]]: top-level synthesis, main themes, and open questions
- [[log]]: chronological record of every operation

## Sources
*(newest first)*
- [[src-qmd-source-code]]: verbatim qmd code excerpts; settled all 3 README contradictions (the README was stale) · commit 04e4dbd, 2026-09-09 · GitHub `tobi`
- [[src-qmd-readme]]: README for qmd, an on-device hybrid search engine for markdown with CLI, MCP, and SDK · snapshot 2026-10-02 · GitHub `tobi`
- [[src-karpathy-llm-wiki]]: Karpathy's idea file describing the LLM-maintained personal wiki pattern · ~2026-04 · [[andrej-karpathy]]

## Entities
- [[andrej-karpathy]]: AI researcher; author of the LLM Wiki idea file · 1 source
- [[obsidian]]: markdown app used as the wiki's browsing front end ("IDE") · 2 sources
- [[qmd]]: local hybrid search (BM25 + vector + rerank) for markdown, used by agents via CLI/MCP; README checked against the code · 3 sources
- [[vannevar-bush]]: originator of the Memex (1945) · 1 source

## Concepts
- [[document-chunking]]: splitting docs for embedding and reranking; qmd's ~900-token, heading-aware chunks · 2 sources
- [[hybrid-search]]: BM25 + vector search, fused and re-ranked; skips LLM expansion when BM25 is already confident · 3 sources
- [[llm-wiki]]: an LLM incrementally builds and maintains a persistent, interlinked wiki from raw sources · 2 sources
- [[maintenance-burden]]: why human-run wikis die (bookkeeping), and why LLMs fix that · 1 source
- [[memex]]: Bush's 1945 vision of a private, curated store with associative trails · 1 source
- [[model-context-protocol]]: how agents call tools like qmd natively instead of via CLI · 2 sources
- [[reciprocal-rank-fusion]]: merging ranked lists via Σ1/(k+rank); qmd uses k=60 plus bonuses · 2 sources
- [[retrieval-augmented-generation]]: query-time chunk retrieval; the non-compounding contrast to an LLM wiki · 2 sources

## Analyses
- [[qmd-setup-for-this-wiki]]: when to adopt qmd (not yet, ~100 sources) and the exact 3-step setup + gotchas · 2 sources
