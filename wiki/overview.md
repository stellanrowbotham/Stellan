---
type: overview
title: Overview
aliases: ["Second brain overview", "Synthesis"]
tags: [meta]
created: 2026-10-01
updated: 2026-10-02
sources: [src-karpathy-llm-wiki, src-qmd-readme]
---

# Overview
The top-level synthesis of Stellan's second brain. It is rewritten (not appended to) as understanding changes.

## What this wiki is
A personal knowledge base built on the [[llm-wiki]] pattern ([[src-karpathy-llm-wiki]]). Stellan curates sources into `raw/`, and Claude compiles them into this interlinked wiki under the rules in `CLAUDE.md`. Browse it in [[obsidian]]. Start with [[index]], and see [[log]] for what happened recently. `tools/wiki.py` provides search, lint, and stats from the terminal.

## Current state (2 sources)
The only domain so far is **meta**: how this second brain works, and the retrieval technology underneath tools like it.
- **Core thesis:** knowledge should be *compiled once and kept current*, not re-derived on every question as in [[retrieval-augmented-generation|RAG]]. The approach is viable because LLMs remove the [[maintenance-burden]] that kills human-run wikis. The idea goes back to the [[memex]] of [[vannevar-bush]] ([[src-karpathy-llm-wiki]]).
- **Refinement after source 2:** the LLM Wiki doesn't reject retrieval; it changes *what* gets retrieved. Once the wiki is large, a local [[hybrid-search]] engine such as [[qmd]] can search the compiled pages. It runs on-device on ~2 GB of models ([[src-qmd-readme]]). So "wiki vs. RAG" turns out to be layering rather than a contradiction *(synthesis)*.

## Main themes
| Theme | Key pages | Sources |
|---|---|---|
| Personal knowledge management with LLMs | [[llm-wiki]], [[maintenance-burden]], [[retrieval-augmented-generation]] | 2 |
| Search & retrieval technology | [[hybrid-search]], [[reciprocal-rank-fusion]], [[document-chunking]], [[qmd]] | 1 |
| Agent tooling | [[model-context-protocol]], [[qmd]], [[obsidian]] | 2 |
| History of knowledge tools | [[memex]], [[vannevar-bush]] | 1 |

## Open questions / gaps
- **What domains should this second brain cover?** Personal goals and health, research topics, books, work? This is still the biggest decision, and the schema may gain subfolders.
- Ingest Vannevar Bush's "As We May Think" (1945) to confirm the [[memex]] claims that are currently *(unverified)*. The Atlantic and Wikipedia are blocked from the cloud container, so Stellan will need to clip it locally.
- Settle the inconsistencies in qmd's README (the number of expansions, top-30 vs. 40 rerank candidates) by reading `src/llm.ts`. See [[qmd]].
- At what scale does index-only navigation break down? Plan: [[qmd-setup-for-this-wiki]].
- qmd's benchmark is self-reported on a tiny corpus. Look for an independent evaluation of hybrid search vs. BM25 vs. vector.
- Possible future pages: Obsidian Web Clipper, Marp, Dataview, HyDE (hypothetical document embeddings).
