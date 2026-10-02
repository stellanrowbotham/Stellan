---
type: source
title: "qmd source code excerpts (commit 04e4dbd)"
aliases: ["qmd code", "qmd src/llm.ts", "qmd src/store.ts"]
tags: [tool, search, primary-source, code]
created: 2026-10-02
updated: 2026-10-02
sources: [src-qmd-source-code]
author: tobi (GitHub)
published: commit 04e4dbd, 2026-09-09
raw: raw/2026-10-02-qmd-source-excerpts.md
---

# qmd source code excerpts (commit 04e4dbd)
> **Raw:** `raw/2026-10-02-qmd-source-excerpts.md` · **Author:** GitHub user `tobi` and contributors · **Published:** commit `04e4dbd`, 2026-09-09 · **Ingested:** 2026-10-02 · **License:** MIT

## TL;DR
These are primary-source excerpts from [[qmd]]'s TypeScript code, pulled to settle the 3 inconsistencies found in [[src-qmd-readme]] (lint finding #2, 2026-10-02). **The code wins all three, and the README is out of date in each case.** The code also shows two behaviours the README doesn't describe: a BM25 "strong signal" shortcut that skips LLM expansion, and reranking on chunks rather than whole documents.

## Key points
- **Rerank candidates = 40.** `RERANK_CANDIDATE_LIMIT = 40`, and the code applies `fused.slice(0, candidateLimit)` (store.ts:430, 5678). The README's "Top 30" is stale.
- **The number of query expansions varies.** `expandQuery` asks the fine-tuned model to "Expand this search query" under a grammar of `lex:`/`vec:`/`hyde:` lines (up to 600 tokens). It keeps every line that contains at least one original query term (llm.ts:1645–1702). So neither the README's "1 variation" nor its "2 alternatives" is right. If no lines survive, the fallback is 3 queryables (hyde, lex, vec). If the model fails, the fallback is lex + vec of the raw query.
- **Strong-signal bypass (undocumented).** An initial BM25 probe runs first. If the top score is ≥ 0.85 *and* leads the runner-up by ≥ 0.15, expansion is skipped entirely. Passing an `intent` turns this shortcut off (store.ts:426–427, 5557–5578).
- **Original query weight = 2.0, expansions 1.0** (`getHybridRrfWeights`, store.ts:5521–5522). This confirms the README.
- **Routing:** original → vector (its FTS results are reused from the probe), `lex` → FTS, `vec`/`hyde` → vector (pipeline comment, store.ts:5527–5534).
- **Reranking runs on chunks, not full bodies.** The code picks the best keyword-matching chunk for each document and reranks that, and its comment warns of an "O(tokens) trap" (store.ts:5532–5533).
- **The MCP `multi_get` maxBytes default is 64 KB** (`DEFAULT_MULTI_GET_MAX_BYTES = 64 * 1024`, used by mcp/server.ts:526). The README's MCP table value of 10240 is stale.
- **Design note in a code comment:** caller `intent` is kept *out* of the expansion prompt, because the model would echo it back as useless sub-queries. Intent shapes reranking and snippet choice instead (llm.ts:1641–1645).

## Notable quotes
> "Step 1: BM25 probe — strong signal skips expensive LLM expansion" (store.ts)

> "rerank on chunks (NOT full bodies — O(tokens) trap)" (store.ts, hybridQuery doc comment)

## How it connects
- ✅ **Resolves** all 3 open contradictions on [[qmd]]. They are marked resolved there, with this page as the citation.
- **Refines** [[hybrid-search]] (the strong-signal shortcut, chunk-level reranking) and [[reciprocal-rank-fusion]] (weights confirmed in code).
- **Lesson for this wiki** *(synthesis)*: a README is a secondary source about its own code. When documentation and implementation disagree, the wiki should cite the code and date it, because both change over time.

## Pages touched by this ingest
- [[qmd]]: tensions resolved, new facts added
- [[hybrid-search]]: strong-signal bypass, chunk-level rerank
- [[reciprocal-rank-fusion]]: weights confirmed in code
- [[document-chunking]]: chunks are also the unit of reranking
- [[src-qmd-readme]]: inconsistencies marked resolved
- [[overview]], [[index]], [[log]]: updated
