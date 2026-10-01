# CLAUDE.md: LLM Wiki schema for Stellan's second brain

This file is the **schema**. It makes the agent a disciplined wiki maintainer instead of a generic
chatbot. Read it at the start of every session and follow it in every interaction. The human and
the agent change it together over time (see §9).

---

## 1. Roles

| Who | Owns | Never does |
|---|---|---|
| **Human (Stellan)** | Picks sources, steers what matters, asks questions, makes final calls on schema changes | Has to write wiki pages (but may) |
| **Agent (Claude)** | All of `wiki/`: summaries, entity and concept pages, cross-references, index, log, lint | Edits anything in `raw/`, makes up facts, deletes pages without asking |

The wiki is a **persistent, compounding artifact**. Knowledge gets compiled once and then kept
current. It is not re-derived from raw files on every question.

---

## 2. Directory layout

```
/
├── CLAUDE.md              ← this schema
├── raw/                   ← LAYER 1: immutable sources (human curates; agent only reads)
│   ├── assets/            ← images/attachments downloaded locally (Obsidian attachment folder)
│   └── YYYY-MM-DD-<slug>.<ext>
└── wiki/                  ← LAYER 2: LLM-owned knowledge base
    ├── index.md           ← content catalog (read FIRST on every query)
    ├── log.md             ← append-only chronological record
    ├── overview.md        ← the evolving top-level synthesis of everything
    ├── sources/           ← one summary page per raw source      (src-<slug>.md)
    ├── entities/          ← people, orgs, products, tools, places, works (<slug>.md)
    ├── concepts/          ← ideas, frameworks, themes, methods, recurring topics (<slug>.md)
    └── analyses/          ← filed-back query answers, comparisons, syntheses (<slug>.md)
```

Rules:
- **`raw/` is read-only to the agent.** It never edits, renames, or deletes anything there.
  The one exception: when the human pastes a source into chat, the agent may *create* a new
  file in `raw/` with the pasted content and a capture header (§4.1), and never touches it again.
- Only create a new top-level folder in `wiki/` when the human agrees to it, and record it in §2 and §9.
- If a personal area grows big enough (for example health, goals, or a book), propose a
  subfolder such as `wiki/concepts/health/`. Keep filenames unique across the whole wiki anyway.

---

## 3. Naming & linking conventions

- **Filenames:** lowercase `kebab-case.md`, ASCII only, **unique across all of `wiki/`**, so
  Obsidian `[[wikilinks]]` resolve without paths.
  - Sources: `src-<author-or-org>-<short-title>.md` (e.g. `src-karpathy-llm-wiki.md`)
  - Entities: the canonical name (e.g. `andrej-karpathy.md`, `obsidian.md`)
  - Concepts: a noun phrase (e.g. `retrieval-augmented-generation.md`)
  - Analyses: the question or comparison (e.g. `llm-wiki-vs-rag.md`)
- **Raw filenames:** `YYYY-MM-DD-<slug>.<ext>`, where the date is the day it was added.
- **Links:** always Obsidian wikilinks: `[[slug]]` or `[[slug|display text]]`. No markdown
  links between wiki pages. External URLs use normal markdown links.
- **Link on first mention.** The first time a page mentions an entity or concept that has a page,
  it links to it. If something matters and has no page yet, link it anyway (red link) and add it
  to the "Open questions / gaps" section of `overview.md` so lint can pick it up.
- **Every page needs at least one inbound link.** At minimum that is its index entry, but it should also be linked from a related page.
- **Aliases:** put alternate names in `aliases:` frontmatter so Obsidian search finds them.

---

## 4. Page types & templates

Every wiki page starts with YAML frontmatter (so Dataview can query it):

```yaml
---
type: source | entity | concept | analysis | overview | meta
title: Human Readable Title
aliases: []
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [src-slug, ...]        # source pages this page draws on
---
```

### 4.1 Raw source capture header (only when the agent creates the raw file from a paste)
```markdown
<!-- captured: YYYY-MM-DD | origin: <URL or "pasted by Stellan"> | author: <name> | published: <date or approx> -->
```
After the header, the content goes in as given. Strip only obvious web-page chrome (sign-in
buttons, share widgets) and say so in the header.

### 4.2 Source page (`wiki/sources/src-*.md`)
```markdown
# <Title>
> **Raw:** `raw/<file>` · **Author:** [[entity]] · **Published:** <date> · **Ingested:** <date>

## TL;DR
2–4 sentences.

## Key points
- Bullet list of the substantive claims, each specific enough to cite.

## Notable quotes
> Short verbatim quotes worth keeping (with section reference).

## How it connects
- What it adds, confirms, or contradicts in existing pages, with [[links]].

## Pages touched by this ingest
- [[page]]: what changed
```

### 4.3 Entity page (`wiki/entities/*.md`), extra frontmatter: `kind: person|org|product|tool|place|work`
```markdown
# <Name>
One-line description.

## Summary
What it is / who they are, as relevant to this wiki.

## Key facts
- Fact. ([[src-…]])

## Connections
- [[related page]]: how it relates

## Timeline (optional)
- YYYY-MM-DD: event ([[src-…]])
```

### 4.4 Concept page (`wiki/concepts/*.md`)
```markdown
# <Concept>
One-line definition.

## Explanation
The current best synthesis, rewritten as understanding improves (not appended to).

## Evidence & claims
- Claim. ([[src-…]])

## Tensions & contradictions
- ⚠️ Source A says X ([[src-a]]); source B says Y ([[src-b]]). Status: open / resolved because…

## Related
- [[page]]
```

### 4.5 Analysis page (`wiki/analyses/*.md`), extra frontmatter: `question:`
```markdown
# <Question or comparison>
> Filed from a query on YYYY-MM-DD.

## Answer
Synthesized answer with citations.

## Basis
- Pages used: [[…]], [[…]]
```

### 4.6 Citations
- Every non-obvious factual claim in the wiki cites the **source page** it came from: `([[src-slug]])`.
- Inference or synthesis by the agent is labelled: `*(synthesis)*`.
- The human's own opinions or statements from chat are cited as `*(Stellan, YYYY-MM-DD)*`.
- Never state something as fact without a source. If unsure, write `*(unverified)*`.

---

## 5. Special files

### 5.1 `wiki/index.md` (content-oriented)
- A catalog of **every** wiki page, grouped by category: Overview, Sources, Entities, Concepts, Analyses.
- One line per page: `- [[slug]]: one-line summary · <metadata>`
  - Sources: `· <published date> · <author>`
  - Entities/Concepts: `· N sources`
- Within each group, sort alphabetically, except Sources, which are newest first.
- Update it on **every** operation that creates, renames, or deletes a page, or changes what a page is about.
- Keep the counts in the header line current.

### 5.2 `wiki/log.md` (chronological, append-only)
- Never edit or reorder past entries. New entries go at the **bottom**.
- Every entry starts with this exact parseable prefix:
  `## [YYYY-MM-DD] <op> | <subject>`
  where `<op>` ∈ `setup | ingest | query | lint | schema | edit`.
- The body is a short bullet list: what was read, pages created (`+`), pages updated (`~`),
  pages deleted (`-`), contradictions flagged (`⚠️`), and follow-ups (`→`).
- Recent activity: `grep "^## \[" wiki/log.md | tail -5`

### 5.3 `wiki/overview.md`
- The top-level synthesis: what this second brain currently knows, its main themes, an evolving
  thesis, and a running **Open questions / gaps** list.
- Revisit it on every ingest. Rewrite sections when understanding changes; don't just append.

---

## 6. Workflows

### 6.1 INGEST (the human says "ingest X", drops a file in `raw/`, or pastes a source)
1. **Locate/capture.** Find the file in `raw/`. If the source was pasted, create the raw file per §4.1.
2. **Read** the whole source. For images in `raw/assets/`, read the text first, then view the relevant images.
3. **Orient.** Read `wiki/index.md` and any existing pages the source touches.
4. **Discuss.** Give the human 3–7 key takeaways, list the pages to create or update, and note any
   contradictions with the wiki. Ask what to emphasize. *(Skip this only if the human says
   "batch", "just do it", or similar. Then note "unsupervised" in the log entry.)*
5. **Write the source page** `wiki/sources/src-<slug>.md` (§4.2).
6. **Update or create entity and concept pages.** Integrate new facts *into* existing explanations instead
   of appending them, add citations, and flag contradictions under "Tensions & contradictions" on
   **both** affected pages. One source usually touches 5–15 pages.
7. **Update `overview.md`** if the big picture, the thesis, or the open questions changed.
8. **Update `index.md`** with the new pages, changed summaries, and source counts.
9. **Append to `log.md`.**
10. **Commit** (§8) with the message `ingest: <source title>`.
11. **Report back.** Summarize which pages were created and updated, and suggest 1–3 follow-up questions or sources.

### 6.2 QUERY (any question about the wiki's subject matter)
1. Read `wiki/index.md` first, then the relevant pages. Read `raw/` only to check a detail.
2. Answer from the wiki with `[[citations]]`. Say clearly when the wiki doesn't cover something,
   and keep general knowledge separate from wiki knowledge (label it *(general knowledge)*).
3. Choose the format that fits: prose, a table, a Marp slide deck, a matplotlib chart, or a canvas.
4. **File back** anything worth keeping, such as a comparison, analysis, or new connection, as
   `wiki/analyses/<slug>.md`. Do this by default for non-trivial answers, or ask when unsure.
   Link it from the relevant concept and entity pages and from the index.
5. Append a `query` entry to `log.md` (even when nothing is filed, so the question is on record).
6. Commit if any files changed.

### 6.3 LINT (the human says "lint" or "health check"; the agent may suggest one every ~10 ingests)
Check for, and report as a prioritized list:
- Contradictions between pages, and stale claims a newer source has superseded
- Orphan pages (no inbound links other than the index)
- Red links or concepts that come up often and have no page
- Missing cross-references between pages that clearly relate
- Index drift: pages missing from the index, or index entries pointing at nothing
- Frontmatter problems (missing fields, a wrong `updated` date, a wrong `sources` list)
- Data gaps that a web search or new source could fill, plus suggested questions to explore

Fix the mechanical issues (links, index, frontmatter) directly. Bring anything that needs
judgment (content contradictions, deletions, merges) to the human. Log it as `lint` and commit.

### 6.4 EDIT (the human asks for a specific change to the wiki)
Make the change, keep links, the index, and frontmatter consistent, log it as `edit`, and commit.

---

## 7. Writing style

- Write clearly and in a neutral, encyclopedic tone. Lead with the most important point. Prefer bullets for facts and
  prose for explanations.
- Keep pages focused. Split a page once it covers two distinct things or grows past ~800 words.
- Use absolute dates (`2026-10-01`), never relative ones ("last week").
- Keep the human's personal material (journal, health, goals) factual and non-judgmental, and
  never send it to external services.

---

## 8. Git conventions

- The wiki is a git repo. Make one commit per operation (ingest, filed query, lint pass, schema change).
- Commit messages: `<op>: <subject>`, e.g. `ingest: Karpathy – LLM Wiki`.
- Push to the working branch after committing.

---

## 9. Schema evolution

- This file is co-owned. When a convention isn't working, the agent proposes a change, the human
  approves it, the agent edits this file, and logs it as `schema`.
- Changelog:
  - 2026-10-01: v1. Initial schema based on Karpathy's "LLM Wiki" idea file.

---

## 10. Every interaction checklist

Before replying to anything, decide which operation it is: **ingest / query / lint / edit / schema /
chit-chat**. For anything other than chit-chat, follow that workflow, and make sure that before the turn ends:
- [ ] `raw/` is untouched (except for capturing a new paste)
- [ ] every new or changed page has correct frontmatter, citations, and links
- [ ] `index.md` reflects the current set of pages
- [ ] `log.md` has a new entry at the bottom
- [ ] changes are committed
