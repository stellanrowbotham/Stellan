---
type: concept
title: Document chunking
aliases: ["chunking", "smart chunking", "AST-aware chunking"]
tags: [retrieval, embeddings]
created: 2026-10-02
updated: 2026-10-02
sources: [src-qmd-readme]
---

# Document chunking
Splitting documents into smaller pieces before embedding them, so that vector search can match passages rather than whole files.

## Explanation
Embedding models have limited context, and one vector for a long document blurs its topics together. Retrieval systems therefore split documents into **chunks**. The design question is where to cut, because a cut through the middle of a section or a code block destroys meaning ([[src-qmd-readme]]).

[[qmd]]'s "smart chunking" ([[src-qmd-readme]]):
- Target ~**900 tokens** per chunk, with **15% overlap**.
- Score candidate break points: H1 = 100, H2 = 90, H3 = 80 … H6 = 50, a code fence = 80, a horizontal rule = 60, a blank line = 20, a list item = 5, a line break = 1.
- Search a **200-token window** before the target and pick the break point with the highest `base × (1 − (distance/window)² × 0.7)`. A heading 200 tokens back still beats a bare line break at the target.
- Never cut inside a code fence.
- For code files (`.ts .js .py .go .rs`), there is optional **AST-aware** chunking via tree-sitter, which breaks at class and function boundaries.

**Implication for this wiki** *(synthesis)*: well-sectioned pages with clear `##` headings and focused topics, as `CLAUDE.md` §7 already requires, chunk cleanly. That makes them easier to retrieve once search is added. The schema's ~800-word page cap means most pages fit in a single chunk.

## Evidence & claims
- Chunk parameters as above. ([[src-qmd-readme]])

## Tensions & contradictions
- None yet.

## Related
- [[hybrid-search]]
- [[retrieval-augmented-generation]]
- [[qmd]]
