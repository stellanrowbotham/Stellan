---
type: concept
title: LLM Wiki
aliases: ["LLM Wiki pattern", "LLM-maintained wiki", "compiled knowledge base"]
tags: [pkm, llm, knowledge-management]
created: 2026-10-01
updated: 2026-10-02
sources: [src-karpathy-llm-wiki, src-qmd-readme]
---

# LLM Wiki
A personal knowledge-base pattern in which an LLM agent incrementally writes and maintains a persistent, interlinked markdown wiki built from a curated set of raw sources.

## Explanation
Usually people point an LLM at a pile of documents and let it pull fragments at question time ([[retrieval-augmented-generation]]). The LLM Wiki pattern adds a compiled middle layer instead. Each time a source comes in, the agent reads it and **integrates** it into the existing pages. It revises summaries, updates entity pages, adds cross-references, and flags contradictions. Synthesis then happens at write time, once, rather than at read time on every question. The wiki becomes a **compounding artifact**: every source and every filed-back answer makes it richer ([[src-karpathy-llm-wiki]]).

The pattern has three layers ([[src-karpathy-llm-wiki]]):

| Layer | Owner | Mutability |
|---|---|---|
| Raw sources | Human curates | Immutable source of truth |
| Wiki | LLM writes | Constantly revised |
| Schema (CLAUDE.md / AGENTS.md) | Co-evolved | Changes as the workflow matures |

It also has three operations: **ingest**, **query** (with good answers filed back), and **lint** ([[src-karpathy-llm-wiki]]). Two files help with navigation: `index.md`, a content catalog, and `log.md`, a chronological record.

It works because the LLM takes on the part of knowledge work that people give up on, the bookkeeping. See [[maintenance-burden]]. In spirit it continues [[vannevar-bush]]'s [[memex]] ([[src-karpathy-llm-wiki]]).

The suggested setup is the agent in one window and [[obsidian]] in the other, used for browsing, graph view, and Dataview. Once the wiki outgrows the index, add a search tool such as [[qmd]] ([[src-karpathy-llm-wiki]]). qmd provides local [[hybrid-search]], and the agent can call it from the CLI or as a native tool over [[model-context-protocol|MCP]] ([[src-qmd-readme]]).

## Evidence & claims
- An index-first approach without embeddings "works surprisingly well at moderate scale (~100 sources, ~hundreds of pages)." ([[src-karpathy-llm-wiki]])
- A single ingest might touch 10–15 wiki pages. ([[src-karpathy-llm-wiki]])
- It applies to personal tracking, research, reading companions, team wikis, due diligence, trip planning, and course notes. ([[src-karpathy-llm-wiki]])
- This repo (Stellan's second brain) is an instance of the pattern, set up 2026-10-01. *(Stellan, 2026-10-01)*

## Tensions & contradictions
- *(synthesis)* The scale limit is an open question. Past a few hundred pages, an index-only approach probably needs search such as [[qmd]], and that brings back part of the retrieval machinery the pattern set out to avoid. No source has tested where that threshold is yet. **Update 2026-10-02:** [[src-qmd-readme]] shows the retrieval layer can run entirely on-device on ~2 GB of models. So the cost of adding search is low, though the threshold itself is still untested. Plan: [[qmd-setup-for-this-wiki]].
- *(synthesis)* Errors can compound as well. If the LLM writes a wrong synthesis, later ingests may build on it. Citations back to `raw/` and regular lint passes are the safeguard.

## Related
- [[retrieval-augmented-generation]]: the contrast case
- [[maintenance-burden]]: why it works
- [[memex]]: historical precedent
- [[andrej-karpathy]]: who described the pattern
- [[qmd]], [[hybrid-search]]: the scale-up path
