---
type: concept
title: Reciprocal Rank Fusion (RRF)
aliases: ["RRF"]
tags: [retrieval, search, algorithm]
created: 2026-10-02
updated: 2026-10-02
sources: [src-qmd-readme]
---

# Reciprocal Rank Fusion (RRF)
A method for merging several ranked result lists by summing `1/(k + rank)` for each document across the lists, ignoring the backends' raw scores.

## Explanation
Different search backends produce scores on scales that can't be compared directly. BM25 is unbounded, while cosine similarity is bounded. RRF sidesteps this by using only each document's **rank** in each list. A document that ranks well in several lists ends up near the top ([[src-qmd-readme]]).

[[qmd]]'s version ([[src-qmd-readme]]):
- `score = Σ 1/(k + rank + 1)` with **k = 60**
- The original query's lists get **×2 weight** compared with the LLM-expanded variants.
- **Top-rank bonus:** +0.05 for a #1 in any list, +0.02 for #2–3.
- The top candidates then go to an LLM reranker, and the two scores are blended by rank position (75/25 for ranks 1–3, 60/40 for 4–10, 40/60 for 11+).

**Why the bonus and the blend exist:** "Pure RRF can dilute exact matches when expanded queries don't match" ([[src-qmd-readme]]). The fix is to protect strong hits from the original query.

## Evidence & claims
- k=60 is qmd's chosen constant. ([[src-qmd-readme]])
- *(general knowledge, unverified here)* RRF was introduced by Cormack, Clarke & Büttcher (SIGIR 2009), where k=60 is the commonly cited default.

## Tensions & contradictions
- None yet.

## Related
- [[hybrid-search]]
- [[qmd]]
