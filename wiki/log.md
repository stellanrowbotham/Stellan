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

## [2026-10-02] schema | v1.1: add tools/wiki.py
- + `tools/wiki.py`, a stdlib-only CLI with `search` (BM25 over wiki pages, titles and aliases weighted ×3), `lint` (broken links, orphans, index drift, frontmatter, raw files not yet ingested), `stats`, and `graph` (JSON export)
- ~ `CLAUDE.md`: §2 layout, §6.2 query (search step), §6.3 lint (run the script first), §9 changelog, §10 checklist
- → This is the "naive search script" from [[src-karpathy-llm-wiki]]; graduate to [[qmd]] per [[qmd-setup-for-this-wiki]]

## [2026-10-02] query | How and when should we plug qmd into this wiki?
- Read: [[index]], then `tools/wiki.py search` → [[src-qmd-readme]], [[llm-wiki]], [[model-context-protocol]], [[overview]], [[qmd]]; also [[hybrid-search]], [[document-chunking]]
- + [[qmd-setup-for-this-wiki]] (filed back; resolves the red link from the qmd ingest)
- ~ [[index]], [[hybrid-search]], [[document-chunking]] (linked to the analysis)
- Answer: not yet (2/~100 sources). The setup is a project-local index, `raw/` excluded by default, and a context tree that mirrors CLAUDE.md §2
- ⚠️ Cross-source finding: qmd can't filter on our plain frontmatter
- → Proposed schema change (awaiting Stellan): add qmd to the ingest and query steps once a trigger is hit
- Also: `tools/wiki.py search` now skips meta pages (index/log) by default, since they outranked real pages

## [2026-10-02] lint | First health check (2 sources, 18 pages)
- Ran `tools/wiki.py lint`: ✓ clean (0 broken links, 0 orphans, 0 index drift)
- ~ `tools/wiki.py`: lint now also checks the "· N sources" counts in the index against frontmatter (tested by planting a wrong count, then reverted)
- ~ [[hybrid-search]]: removed the "BM25" alias. BM25 is one *component* of hybrid search, not a synonym, so the alias would send searches for BM25 to the wrong page.
- Findings for Stellan, in priority order:
  1. ⚠️ **6 *(unverified)* general-knowledge claims** need a source: [[andrej-karpathy]] (Tesla/OpenAI roles), [[vannevar-bush]] (OSRD), [[memex]] ("As We May Think", *The Atlantic*), [[reciprocal-rank-fusion]] (Cormack et al. 2009), [[model-context-protocol]] (Anthropic, 2024), [[qmd]] (`tobi` = Tobi Lütke)
  2. ⚠️ **3 open contradictions inside the qmd README** on [[qmd]]. Fix: read `src/llm.ts` in tobi/qmd (reachable from this container)
  3. **Single-source pages:** [[memex]], [[vannevar-bush]], [[andrej-karpathy]], [[maintenance-burden]], [[reciprocal-rank-fusion]], [[document-chunking]]
  4. **Concepts mentioned with no page:** HyDE, BM25, Obsidian Web Clipper, Marp, Dataview
  5. **Self-reported benchmark:** the [[hybrid-search]] evidence is qmd's own fixture; an independent evaluation is needed
- → Suggested next sources: "As We May Think" (Bush 1945); the RRF paper (Cormack, Clarke & Büttcher 2009); the MCP spec or announcement; the qmd source `src/llm.ts`

## [2026-10-02] ingest | qmd source code excerpts (commit 04e4dbd)
- Trigger: lint finding #2. GitHub is reachable from the container, so the contradictions could be checked against the primary source right away.
- Read: `src/store.ts`, `src/llm.ts`, `src/mcp/server.ts` at commit `04e4dbd`; verbatim excerpts captured to `raw/2026-10-02-qmd-source-excerpts.md`
- Mode: unsupervised (Stellan's "show me what it can do")
- + [[src-qmd-source-code]]
- ~ [[qmd]], [[src-qmd-readme]], [[hybrid-search]], [[reciprocal-rank-fusion]], [[document-chunking]], [[overview]], [[index]]
- ✅ Resolved all 3 ⚠️ contradictions on [[qmd]]; the README was stale each time (expansions vary, rerank pool 40, MCP multi_get 64 KB)
- New facts the README doesn't cover: the BM25 strong-signal shortcut (≥ 0.85, gap ≥ 0.15) and chunk-level reranking
- → Open: 6 *(unverified)* general-knowledge claims still need sources (see the lint entry above)
