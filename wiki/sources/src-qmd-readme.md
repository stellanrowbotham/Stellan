---
type: source
title: "QMD – Query Markup Documents (README)"
aliases: ["qmd README", "tobi/qmd"]
tags: [tool, search, retrieval, markdown, mcp]
created: 2026-10-02
updated: 2026-10-02
sources: [src-qmd-readme]
author: tobi (GitHub)
published: living document, snapshot 2026-10-02
raw: raw/2026-10-02-qmd-readme.md
---

# QMD – Query Markup Documents (README)
> **Raw:** `raw/2026-10-02-qmd-readme.md` · **Author:** GitHub user `tobi` and contributors · **Published:** living README, snapshot 2026-10-02 · **Ingested:** 2026-10-02 · **License:** MIT

## TL;DR
[[qmd]] is a local, on-device search engine for markdown, built for agent workflows. It combines [[hybrid-search|BM25 keyword search, vector search]], LLM query expansion and LLM re-ranking. Results are fused with [[reciprocal-rank-fusion]] and blended according to their rank position. Everything runs locally on three small GGUF models (~2 GB in total). Agents can use it through a CLI with JSON output, an [[model-context-protocol|MCP]] server, or a Node/Bun SDK. It confirms and fills in the claims made about qmd in [[src-karpathy-llm-wiki]].

## Key points
- **What it is:** "An on-device search engine for everything you need to remember." Its targets are markdown notes, meeting transcripts, docs, and knowledge bases.
- **Three search modes:** `qmd search` uses BM25 only (fast). `qmd vsearch` uses vectors only. `qmd query` runs the full hybrid pipeline with expansion and reranking (best quality).
- **Pipeline:** query expansion (a fine-tuned 1.7B model) → BM25 (SQLite FTS5) and vector search for each query → [[reciprocal-rank-fusion|RRF]] with k=60. The original query gets ×2 weight, and the top-ranked results get a bonus (+0.05 for #1, +0.02 for #2–3) → LLM rerank (qwen3-reranker, yes/no + logprobs) → position-aware blend. Ranks 1–3 are 75% retrieval and 25% reranker, ranks 4–10 are 60/40, and rank 11+ is 40/60.
- **Why the blend:** "Pure RRF can dilute exact matches when expanded queries don't match," and position-aware blending "prevents the reranker from destroying high-confidence retrieval results."
- **Benchmark claim:** on the bundled example fixture, BM25 scores ~0.50, vector ~0.70, and hybrid/full ~1.00. This is offered as evidence that hybrid search beats either backend alone.
- **Models** (auto-downloaded to `~/.cache/qmd/models/`): `embeddinggemma-300M` (~300 MB), `qwen3-reranker-0.6b` (~640 MB), `qmd-query-expansion-1.7B` (~1.1 GB). For multilingual or CJK text, swap in Qwen3-Embedding.
- **[[document-chunking|Chunking]]:** ~900-token chunks with 15% overlap. It prefers natural markdown break points: H1 scores 100, H2 90, and so on, a code fence 80, a blank line 20. The search window is 200 tokens, scores decay with the square of the distance, and code fences are never split. Code files can opt in to AST-aware chunking with tree-sitter.
- **Context tree:** the README calls it "the key feature of QMD." Descriptions attached to collections and paths (`qmd context add qmd://notes "Personal notes"`) are returned with results, which helps LLMs pick documents.
- **Agent interfaces:** CLI `--json`/`--files`/`--md` output, MCP tools (`query`, `get`, `multi_get`, `status`) over stdio or HTTP (`localhost:8181`), and an SDK (`createStore`).
- **Claude Code integration:** `claude plugin marketplace add tobi/qmd` followed by `claude plugin install qmd@qmd`, or configure the MCP server manually.
- **Metadata filtering:** works only with a namespaced `qmd: metadata:` frontmatter block. Matching is exact and typed, and `and` must be written out explicitly.
- **Safety:** the HTTP server rejects non-loopback `Origin` headers, which defends against DNS rebinding. A `.qmd/index.yml` checked into a project is *not trusted* for update commands, paths outside the project, or custom models until `qmd trust` is run.
- **Storage:** a single SQLite file, `~/.cache/qmd/index.sqlite`, with an FTS5 table, sqlite-vec vectors, and an LLM response cache.
- **Requirements:** Node ≥ 22 or Bun ≥ 1.0. On macOS, Homebrew SQLite.

## Notable quotes
> "This is the key feature of QMD as it allows LLMs to make much better contextual choices when selecting documents. Don't sleep on it!" (Quick Start, about context)

> "Pure RRF can dilute exact matches when expanded queries don't match." (Fusion Strategy)

## How it connects
- **Confirms** every qmd claim in [[src-karpathy-llm-wiki]]: hybrid BM25/vector search, LLM re-ranking, on-device, CLI plus MCP server.
- **Adds detail** to [[qmd]] (the full rewrite), [[retrieval-augmented-generation]] (qmd is a modern retrieval stack), and [[llm-wiki]] (a concrete answer to how the pattern scales).
- **New concepts:** [[hybrid-search]], [[reciprocal-rank-fusion]], [[document-chunking]], [[model-context-protocol]].
- ⚠️ **Inconsistencies within the README itself** (both noted on [[qmd]]):
  1. *Number of query expansions:* the architecture diagram says "2 alternative queries" and the Query Flow shows `[Original, Variant 1, Variant 2]`, but Fusion Strategy says "Original query (×2 for weighting) + 1 LLM variation."
  2. *Rerank candidate count:* the diagram and Fusion Strategy say "Top 30," while the `candidateLimit`/`-C` default is 40.
  3. *(minor)* `multi_get` `maxBytes` defaults to 10240 in the MCP tool table but to 64 KB in the CLI and SDK.
- **Tension with this wiki's schema:** qmd's metadata filters ignore plain YAML frontmatter like ours. See [[qmd-setup-for-this-wiki]].

## Pages touched by this ingest
- [[qmd]]: rewritten with full detail, an inconsistency list, and a status update
- [[hybrid-search]], [[reciprocal-rank-fusion]], [[document-chunking]], [[model-context-protocol]]: created
- [[retrieval-augmented-generation]]: added qmd as a worked example of a modern retrieval stack
- [[llm-wiki]]: scale tension updated
- [[obsidian]]: link to qmd as a complementary tool kept and clarified
- [[overview]], [[index]], [[log]]: updated
