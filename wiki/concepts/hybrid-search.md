---
type: concept
title: Hybrid search
aliases: ["hybrid retrieval", "BM25 + vector search", "BM25"]
tags: [retrieval, search]
created: 2026-10-02
updated: 2026-10-02
sources: [src-qmd-readme, src-karpathy-llm-wiki]
---

# Hybrid search
Retrieval that runs keyword search (BM25) and semantic vector search together and fuses their rankings, often followed by an LLM re-ranking step.

## Explanation
The two backends fail in different ways. **BM25** (full-text keyword scoring, e.g. SQLite FTS5) is fast and exact, but it misses paraphrases. **Vector search** (embedding similarity) finds things with the same meaning but can miss exact names and identifiers. Hybrid search runs both and merges their ranked lists, usually with [[reciprocal-rank-fusion]], so the merged list keeps each backend's strengths ([[src-qmd-readme]]).

Modern pipelines such as [[qmd]] add two LLM stages ([[src-qmd-readme]]):
1. **Query expansion:** an LLM rewrites the query into variants. Keyword-style variants (`lex`) go to BM25. Dense sentences (`vec`) and hypothetical answer documents (`hyde`) go to vector search.
2. **Re-ranking:** a small cross-encoder LLM scores the top candidates for relevance. qmd blends the reranker score with the retrieval score according to rank, so a strong exact match isn't overruled.

Karpathy names hybrid BM25/vector search with LLM re-ranking as the right search upgrade once an [[llm-wiki]] outgrows its index ([[src-karpathy-llm-wiki]]).

## Evidence & claims
- On qmd's example fixture, BM25 scores ~0.50, vector ~0.70, and hybrid/full ~1.00. ([[src-qmd-readme]]) *(synthesis: this is the tool author's own benchmark on a small bundled corpus. Treat it as illustrative, not as independent evidence.)*
- BM25 score ranges are unbounded (0 to ~25+), so fusion uses *ranks* rather than raw scores. ([[src-qmd-readme]])

## Tensions & contradictions
- None between sources yet. The benchmark caveat above is the main open point.

## Related
- [[reciprocal-rank-fusion]]
- [[document-chunking]]
- [[retrieval-augmented-generation]]
- [[qmd]]
- [[qmd-setup-for-this-wiki]]: how this wiki will adopt it
