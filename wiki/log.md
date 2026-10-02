---
type: meta
title: Log
tags: [meta]
created: 2026-10-01
---

# Log
Append-only. Newest entries at the bottom. Each entry starts with `## [YYYY-MM-DD] op | subject`.
Last 5 entries: `grep "^## \[" wiki/log.md | tail -5`

## [2026-10-01] setup | Second brain initialized
- Created the schema `CLAUDE.md` (v1), based on Karpathy's LLM Wiki idea file
- Created folders: `raw/`, `raw/assets/`, `wiki/{sources,entities,concepts,analyses}/`
- + [[index]], [[log]], [[overview]]

## [2026-10-01] ingest | LLM Wiki (Karpathy idea file)
- Read: `raw/2026-10-01-karpathy-llm-wiki.md` (captured from Stellan's paste; GitHub chrome stripped)
- Mode: demonstration ingest. Takeaways were presented after writing rather than discussed first, at Stellan's request to see a full example.
- + [[src-karpathy-llm-wiki]]
- + [[llm-wiki]], [[retrieval-augmented-generation]], [[maintenance-burden]], [[memex]]
- + [[andrej-karpathy]], [[vannevar-bush]], [[obsidian]], [[qmd]]
- ~ [[overview]] (initial synthesis), [[index]]
- ⚠️ No contradictions (first source). Two *(synthesis)* tensions noted on [[llm-wiki]]: the scale limit and compounding errors
- → Decide which domains this second brain covers; ingest "As We May Think" (Bush, 1945) to confirm the Memex claims

## [2026-10-02] ingest | QMD – Query Markup Documents (README)
- Read: `raw/2026-10-02-qmd-readme.md` (fetched from github.com/tobi/qmd; MIT; verbatim)
- Mode: unsupervised. Stellan said "make the brain and show me what it can do," so there was no takeaway discussion first.
- + [[src-qmd-readme]]
- + [[hybrid-search]], [[reciprocal-rank-fusion]], [[document-chunking]], [[model-context-protocol]]
- ~ [[qmd]] (rewritten with full detail; the Karpathy claims about it are now confirmed), [[retrieval-augmented-generation]], [[llm-wiki]], [[obsidian]], [[overview]], [[index]]
- ⚠️ 3 inconsistencies within the README itself, logged on [[qmd]]: expansion count 1 vs. 2, rerank pool 30 vs. 40, multi_get max bytes 10 KB vs. 64 KB
- ⚠️ Schema tension: qmd metadata filters need a `qmd: metadata:` block, but our frontmatter is plain YAML
- → Red link [[qmd-setup-for-this-wiki]], to be filled by a query; read qmd `src/llm.ts` to settle the inconsistencies
- Note: tried to fetch Wikipedia "Memex" first. The cloud network policy blocked it, so a GitHub-hosted source was used instead.
