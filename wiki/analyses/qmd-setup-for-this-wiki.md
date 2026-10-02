---
type: analysis
title: "When and how to add qmd to this wiki"
question: "How and when should we plug qmd into this second brain?"
aliases: ["qmd plan", "search upgrade plan"]
tags: [plan, tooling, search]
created: 2026-10-02
updated: 2026-10-02
sources: [src-karpathy-llm-wiki, src-qmd-readme]
---

# When and how to add qmd to this wiki
> Filed from a query on 2026-10-02. Basis: [[qmd]], [[llm-wiki]], [[hybrid-search]], [[document-chunking]], [[model-context-protocol]].

## Answer

### When: not yet
- Karpathy reports that index-first navigation "works surprisingly well" up to **~100 sources / hundreds of pages** ([[src-karpathy-llm-wiki]]). This wiki has 2 sources and 15 pages.
- Until then, `tools/wiki.py search` (naive BM25) covers lookups the index can't. *(synthesis)*
- **Triggers to switch** *(synthesis)*. Any one of these is enough:
  1. ~100 sources, or `index.md` gets too long to read in one pass.
  2. A query misses a page that it should have found. Log these as `query` entries with a "missed" note so the pattern is visible.
  3. A lot of non-English material arrives, which calls for Qwen3-Embedding ([[src-qmd-readme]]).

### How: a 3-step setup (run on Stellan's machine)
Requirements: Node ≥ 22 or Bun ≥ 1.0, ~2 GB disk for the models, and Homebrew SQLite on macOS ([[src-qmd-readme]]).

```sh
npm install -g @tobilu/qmd
cd ~/path/to/Stellan
qmd init                                   # project-local: .qmd/index.yml + index.sqlite

# 1. Two collections: compiled knowledge first, raw sources only on request
qmd collection add wiki --name wiki --mask "**/*.md"
qmd collection add raw  --name raw  --mask "**/*.md"
qmd collection exclude raw                 # unscoped queries hit the wiki; use -c raw to verify

# 2. Context tree: mirror CLAUDE.md §2 ("the key feature", per the README)
qmd context add qmd://wiki/sources   "One summary page per ingested raw source"
qmd context add qmd://wiki/entities  "People, orgs, tools, places, works"
qmd context add qmd://wiki/concepts  "Ideas, frameworks, themes; current best synthesis"
qmd context add qmd://wiki/analyses  "Answers to past questions, filed back"
qmd context add qmd://raw            "Immutable original sources; ground truth"

# 3. Embed, then wire it into Claude Code
qmd embed
claude plugin marketplace add tobi/qmd && claude plugin install qmd@qmd
```
(Commands from [[src-qmd-readme]]. The collection and context layout is *(synthesis)*.)

**Then make these schema changes** (proposal; needs Stellan's OK per `CLAUDE.md` §9):
- Ingest step 8½: run `qmd update && qmd embed` after updating the index.
- Query step 1: use `qmd query` (via [[model-context-protocol|MCP]]) in place of `tools/wiki.py search`.
- Add `.qmd/index.sqlite` to `.gitignore` *(synthesis: it's a rebuildable cache)*.

### Gotchas found by cross-reading the sources
- ⚠️ **Our frontmatter is invisible to qmd's filters.** qmd only filters on a namespaced `qmd: metadata:` block ([[src-qmd-readme]]). Plain `type:`/`tags:` stay searchable as text but can't be filtered. Options: (a) live with it; (b) add a `qmd: metadata: {type, tags}` mirror block to every page, which `tools/wiki.py` could generate. Recommendation: (a) until filtering is actually needed *(synthesis)*.
- **The checked-in config is gated.** A committed `.qmd/index.yml` is trusted for in-project paths only. Update hooks need `qmd trust` once per machine ([[src-qmd-readme]]).
- **Chunking is a non-issue here.** The schema caps pages at ~800 words, so most pages are a single ~900-token chunk, and `##` sections give clean break points ([[document-chunking]]).
- **Don't index `raw/` by default.** Otherwise searches return raw fragments and the agent drifts back into plain [[retrieval-augmented-generation|RAG]]. That defeats the point of the [[llm-wiki]] *(synthesis)*.

## Basis
- Pages used: [[qmd]], [[llm-wiki]], [[hybrid-search]], [[document-chunking]], [[model-context-protocol]], [[retrieval-augmented-generation]]
- Sources: [[src-karpathy-llm-wiki]], [[src-qmd-readme]]
