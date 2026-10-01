---
type: concept
title: Maintenance burden (why wikis die)
aliases: ["wiki maintenance burden", "bookkeeping problem"]
tags: [pkm, knowledge-management]
created: 2026-10-01
updated: 2026-10-01
sources: [src-karpathy-llm-wiki]
---

# Maintenance burden (why wikis die)
The observation that personal and team knowledge bases get abandoned because the cost of keeping them consistent grows faster than the value they provide.

## Explanation
The hard part of keeping a knowledge base is not reading or thinking. It is the **bookkeeping**: updating cross-references, keeping summaries current, noting when new data contradicts old claims, and keeping dozens of pages consistent ([[src-karpathy-llm-wiki]]). People do these chores badly and eventually stop, so the wiki goes stale.

LLMs don't get bored, don't forget to update a cross-reference, and can edit 15 files in one pass. That brings the marginal cost of maintenance close to zero, and the wiki stays maintained ([[src-karpathy-llm-wiki]]). This is the economic argument behind [[llm-wiki]]. It also answers the problem the [[memex]] left open, which was who does the maintenance.

The division of labour that follows ([[src-karpathy-llm-wiki]]):
- **Human:** curate sources, direct the analysis, ask good questions, and think about what it all means.
- **LLM:** everything else.

## Evidence & claims
- "Humans abandon wikis because the maintenance burden grows faster than the value." ([[src-karpathy-llm-wiki]])
- The same mechanism applies to team wikis: "the LLM does the maintenance that no one on the team wants to do." ([[src-karpathy-llm-wiki]])

## Tensions & contradictions
- *(synthesis)* The burden moves rather than disappears. The human still has to review what the LLM writes. Whether that review cost stays low as the wiki grows is untested. Track it in this wiki's own [[log]].

## Related
- [[llm-wiki]]
- [[memex]]
