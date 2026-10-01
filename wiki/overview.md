---
type: overview
title: Overview
aliases: ["Second brain overview", "Synthesis"]
tags: [meta]
created: 2026-10-01
updated: 2026-10-01
sources: [src-karpathy-llm-wiki]
---

# Overview
The top-level synthesis of Stellan's second brain. It is rewritten (not appended to) as understanding changes.

## What this wiki is
A personal knowledge base built on the [[llm-wiki]] pattern ([[src-karpathy-llm-wiki]]). Stellan curates sources into `raw/`, and Claude compiles them into this interlinked wiki under the rules in `CLAUDE.md`. Browse it in [[obsidian]]. Start with [[index]], and see [[log]] for what happened recently.

## Current state (1 source)
The only domain so far is **meta**: how this second brain itself works.
- **Core thesis so far:** knowledge should be *compiled once and kept current*, not re-derived on every question as in [[retrieval-augmented-generation|RAG]]. The approach is viable because LLMs remove the [[maintenance-burden]] that kills human-run wikis. The idea goes back to the [[memex]] of [[vannevar-bush]] ([[src-karpathy-llm-wiki]]).

## Main themes
| Theme | Key pages | Sources |
|---|---|---|
| Personal knowledge management with LLMs | [[llm-wiki]], [[retrieval-augmented-generation]], [[maintenance-burden]] | 1 |
| History of knowledge tools | [[memex]], [[vannevar-bush]] | 1 |
| Tooling | [[obsidian]], [[qmd]] | 1 |

## Open questions / gaps
- **What domains should this second brain cover?** Personal goals and health, research topics, books, work? Decide this, and the schema may gain subfolders.
- Ingest Vannevar Bush's essay "As We May Think" (1945) to confirm the [[memex]] claims that are currently *(unverified)*.
- At what scale does index-only navigation break down, and when should [[qmd]] be added?
- How should review work for the human as the wiki grows? (See [[maintenance-burden]] § Tensions.)
- Possible future pages: Obsidian Web Clipper, Marp, Dataview. These are mentioned in [[obsidian]] but don't have their own pages.
