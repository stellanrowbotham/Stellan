---
type: concept
title: Retrieval-Augmented Generation (RAG)
aliases: ["RAG"]
tags: [llm, retrieval, knowledge-management]
created: 2026-10-01
updated: 2026-10-01
sources: [src-karpathy-llm-wiki]
---

# Retrieval-Augmented Generation (RAG)
An approach where an LLM answers questions by retrieving relevant chunks from a document collection at query time and generating an answer from them.

## Explanation
In the usual RAG setup you upload files, the system retrieves chunks that match the question, and the LLM answers from those chunks. Examples include NotebookLM, ChatGPT file uploads, and most RAG products ([[src-karpathy-llm-wiki]]). It works, but there is **no accumulation**. A question that needs five documents synthesized makes the model find and piece together the fragments again every time ([[src-karpathy-llm-wiki]]).

The [[llm-wiki]] pattern moves synthesis from query time to ingest time. The comparison below is a *(synthesis)* of the source:

| | RAG | LLM Wiki |
|---|---|---|
| When synthesis happens | Every query | Once, at ingest, then maintained |
| Cross-references | Rebuilt each time (if at all) | Persisted as links |
| Contradictions | Rarely surfaced | Flagged on pages |
| Infrastructure | Embeddings + vector store | Markdown + index file (search optional) |
| Human-readable artifact | No | Yes: the wiki itself |

## Evidence & claims
- NotebookLM, ChatGPT file uploads, and most RAG systems work in this re-derive-every-time way. ([[src-karpathy-llm-wiki]])
- At moderate scale, an index file removes the need for embedding-based RAG infrastructure. ([[src-karpathy-llm-wiki]])

## Tensions & contradictions
- *(synthesis)* The two approaches can be combined. Hybrid search over the *wiki* (for example [[qmd]]) is still retrieval, just over compiled pages rather than raw chunks.

## Related
- [[llm-wiki]]
- [[qmd]]
