---
type: source
title: "LLM Wiki (Karpathy idea file)"
aliases: ["LLM Wiki gist", "llm-wiki.md"]
tags: [pkm, llm, knowledge-management, meta]
created: 2026-10-01
updated: 2026-10-01
sources: [src-karpathy-llm-wiki]
author: andrej-karpathy
published: 2026-04 (approx.)
raw: raw/2026-10-01-karpathy-llm-wiki.md
---

# LLM Wiki (Karpathy idea file)
> **Raw:** `raw/2026-10-01-karpathy-llm-wiki.md` · **Author:** [[andrej-karpathy]] · **Published:** ~2026-04 (GitHub gist) · **Ingested:** 2026-10-01

## TL;DR
The gist proposes the [[llm-wiki]] pattern. An LLM agent builds and maintains a persistent, interlinked
markdown wiki that sits between the human and their raw sources, so knowledge is *compiled once and
kept current*. This contrasts with [[retrieval-augmented-generation|RAG]], which re-derives answers from raw chunks on every
question. The human curates and asks questions, and the LLM does all the bookkeeping. This second brain is built on this source.

## Key points
- **The problem with RAG:** NotebookLM, ChatGPT file uploads, and most RAG systems "rediscover knowledge from scratch on every question." Nothing accumulates between questions.
- **The alternative:** the LLM integrates each new source into the wiki. It updates entity pages, revises summaries, flags contradictions, and strengthens or challenges the synthesis.
- **Three layers:** (1) immutable **raw sources**, the source of truth; (2) the LLM-owned **wiki**; (3) the **schema** (CLAUDE.md / AGENTS.md), which the human and the LLM refine together.
- **Three operations:**
  - **Ingest:** read, discuss the takeaways, write a summary, update the index, entity pages, and concept pages, then log it. One source may touch 10–15 pages. Karpathy prefers ingesting one source at a time and staying involved.
  - **Query:** read the index, then the relevant pages, then answer with citations. Good answers get **filed back** as new pages so exploration compounds too.
  - **Lint:** check for contradictions, stale claims, orphans, missing pages and cross-references, and data gaps.
- **Two navigation files:** `index.md` is the content catalog and is read first on queries. It works at ~100 sources / hundreds of pages without embeddings. `log.md` is an append-only timeline with a greppable `## [date] op | title` prefix.
- **Workflow:** the agent edits on one side while [[obsidian]] is open on the other. "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."
- **Optional tooling:** [[qmd]] for local hybrid search once the index stops being enough. Other tools: Obsidian Web Clipper, local image download into `raw/assets/`, graph view, Marp slides, Dataview over frontmatter, and git for history.
- **Why it works:** see [[maintenance-burden]]. Bookkeeping is what kills human-maintained wikis, and for an LLM it costs close to nothing.
- **Lineage:** the gist ties the idea to [[vannevar-bush]]'s [[memex]] (1945). Bush's missing piece was who would do the maintenance.
- **Intentionally abstract:** everything is modular. The specifics are meant to be worked out with your own agent.

## Notable quotes
> "The wiki is a persistent, compounding artifact." (The core idea)

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase." (The core idea)

> "Humans abandon wikis because the maintenance burden grows faster than the value." (Why this works)

> "The human's job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM's job is everything else." (Why this works)

## How it connects
- This is the **founding source** of this wiki. `CLAUDE.md` implements its schema layer, and [[overview]] records that this second brain is an instance of the pattern.
- It sets [[llm-wiki]] against [[retrieval-augmented-generation]], and this wiki now has a concept page for each.
- It brings in [[memex]] and [[vannevar-bush]] as historical precedent.
- No contradictions yet; this is the first source.

## Pages touched by this ingest
- [[llm-wiki]]: created (core concept)
- [[retrieval-augmented-generation]]: created (the contrast case)
- [[maintenance-burden]]: created (the "why it works" argument)
- [[memex]]: created (historical precedent)
- [[andrej-karpathy]]: created (author)
- [[vannevar-bush]]: created (Memex originator)
- [[obsidian]]: created (the viewing/browsing "IDE")
- [[qmd]]: created (optional search tool)
- [[overview]]: initial synthesis written
- [[index]], [[log]]: updated
