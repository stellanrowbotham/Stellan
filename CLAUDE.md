# CLAUDE.md: schema for Stellan's Brain

This file is the **schema** for Stellan's Brain, a personal knowledge base that Claude writes and
maintains (the "LLM Wiki" pattern). Read it at the start of every session and follow it in every
interaction. Stellan and Claude change it together over time (see §10).

The brain has three sections:

| Section | Folder | Hub page | What it's for |
|---|---|---|---|
| **AI Stock & Crypto Investing Apprentice** | `wiki/investing/` | [[investing-apprentice]] | The product Stellan is building: vision, features, roadmap, decisions, market and competitor research |
| **FlowPilot** | `wiki/flowpilot/` | [[flowpilot]] | Stellan's AI automations business: offers, clients, pipeline, tools, operations. Includes [[ace]], the business assistant Stellan uses in Claude chats |
| **Daily Run-Through** | `wiki/daily/` | [[daily-run-through]] | Morning check-ins and end-of-day reviews. The day's items get filed into the other two sections |

[[overview]] is the home page that ties the three sections together.

**The live app:** https://claude.ai/artifact/RmkjrydKPNeqMoYjDdNXm5 shows Stellan's link inbox, agent status and activity, the schedule, the morning breakdown, and a snapshot of each section. Scheduled **agents** (claude.ai Routines) work the inbox every 2 hours and send the 6:30 AM email. Their instructions live in `agents/` (§6.7).

---

## 1. Roles

| Who | Owns | Never does |
|---|---|---|
| **Stellan** | Picks sources, answers check-ins, steers what matters, makes final calls on the schema | Has to write wiki pages (but may) |
| **Claude** | All of `wiki/`: hubs, pages, cross-references, index, log, lint, and running the daily check-ins | Edits files already in `raw/`, makes up facts, deletes pages without asking |

The brain is a **persistent, compounding artifact**. Knowledge gets compiled once and kept current.
It is not re-derived on every question.

---

## 2. Directory layout

```
/
├── CLAUDE.md                 ← this schema
├── tools/wiki.py             ← helper CLI: search · lint · stats · graph (stdlib Python)
├── agents/                   ← standing instructions for the scheduled agents (protocol, inbox, morning brief)
├── raw/                      ← LAYER 1: immutable inputs (Claude only creates new files, never edits)
│   ├── assets/               ← images/attachments (Obsidian attachment folder)
│   ├── daily/                ← Stellan's check-in answers, verbatim: YYYY-MM-DD-morning.md / -evening.md
│   ├── investing/            ← sources for the Apprentice: articles, docs, specs, data exports
│   └── flowpilot/            ← sources for FlowPilot: client briefs, call notes, proposals, ACE chat exports
└── wiki/                     ← LAYER 2: Claude-owned knowledge
    ├── overview.md           ← HOME: Stellan's Brain, the current big picture across all sections
    ├── index.md              ← catalog of every page, grouped by section (read FIRST on every query)
    ├── log.md                ← append-only record of every operation
    ├── sources/              ← one summary page per raw source, any section (src-<slug>.md)
    ├── investing/            ← hub investing-apprentice.md + feature, research, competitor, decision pages
    ├── flowpilot/            ← hub flowpilot.md + ace.md + client, offer, tool, process pages
    └── daily/                ← hub daily-run-through.md + schedule.md + one page per day (daily-YYYY-MM-DD.md)
```

Rules:
- **Files already in `raw/` are never edited, renamed, or deleted.** Claude may *create* new raw
  files to capture something Stellan pasted or answered in chat (§4.1).
- New top-level folders in `wiki/` or `raw/` need Stellan's OK and get recorded here and in §10.
- When a topic inside a section grows large (for example many clients), propose a subfolder
  (`wiki/flowpilot/clients/`). Filenames stay unique across the whole wiki anyway.

---

## 3. Naming & linking conventions

- **Filenames:** lowercase `kebab-case.md`, ASCII only, **unique across all of `wiki/`**, so
  Obsidian `[[wikilinks]]` resolve without paths.
  - Sources: `src-<author-or-org>-<short-title>.md`
  - Daily pages: `daily-YYYY-MM-DD.md`
  - FlowPilot clients: `client-<name>.md`. Offers: `offer-<name>.md`.
  - Apprentice features: `feature-<name>.md`. Decisions: `decision-YYYY-MM-DD-<slug>.md`.
  - Stock/crypto research: `research-<ticker>.md` in `wiki/investing/` (entity, `kind: asset`).
  - Everything else: the canonical name or a noun phrase (`n8n.md`, `dollar-cost-averaging.md`).
- **Raw filenames:** `YYYY-MM-DD-<slug>.<ext>` (the date it was added), inside the right `raw/` subfolder.
- **Links:** always Obsidian wikilinks: `[[slug]]` or `[[slug|display text]]`. External URLs use
  normal markdown links.
- **Link on first mention.** If something matters and has no page yet, link it anyway (a red link)
  and list it under the hub's "Open questions" so it gets filled in.
- **Every page is linked from its section hub** (and from the index).
- **Cross-section links are encouraged.** For example, a FlowPilot automation idea can come from
  an Apprentice feature, or a daily page can link to both sections.

---

## 4. Page types & templates

Every wiki page starts with YAML frontmatter:

```yaml
---
type: hub | entity | concept | analysis | source | daily | overview | meta
section: investing | flowpilot | daily | brain
title: Human Readable Title
aliases: []
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [src-slug, ...]        # source pages this page draws on ([] if none yet)
---
```
Extra fields: entity → `kind: person|org|product|tool|place|work|feature|client|offer|asset`;
analysis → `question:`; source → `raw:`; daily → `raw: [raw/daily/…]` and `date:`.

### 4.1 Raw capture header (when Claude creates a raw file from chat)
```markdown
<!-- captured: YYYY-MM-DD HH:MM | origin: <URL, or "pasted by Stellan", or "check-in answers"> | author: <name> | published: <date or approx> -->
```
Then the content exactly as given. For check-ins, record each question followed by Stellan's
answer word for word (typos included).

### 4.2 Hub page (one per section)
```markdown
# <Section name>
One-line description.

## Snapshot            ← current state in 3–6 bullets, rewritten (not appended) as things change
## <Section-specific blocks>   ← see below
## Open questions      ← unknowns to ask Stellan about at the next check-in
## Pages               ← every page in this section, grouped
```
Section-specific blocks:
- **investing-apprentice:** Vision · Target user · Features (planned / building / shipped) ·
  Tech & data stack · Roadmap · Decisions · Research (markets, strategies, competitors)
- **flowpilot:** What FlowPilot sells · Offers & pricing · Clients & pipeline · Tool stack ·
  Processes · Goals & numbers · ACE
- **daily-run-through:** How it works · Morning questions · Evening questions · Open loops ·
  Entries (newest first)

### 4.3 Entity / concept page
```markdown
# <Name>
One-line description.

## Summary / Explanation     ← current best understanding, rewritten as it improves
## Key facts / Evidence      ← bullets, each cited
## Tensions & contradictions ← ⚠️ A says X, B says Y. Status: open / resolved because…
## Connections               ← [[links]] and how they relate
## Timeline (optional)       ← YYYY-MM-DD: event (citation)
```

### 4.4 Decision page (`decision-YYYY-MM-DD-<slug>`, type `analysis`)
```markdown
# Decision: <what was decided>
> Decided YYYY-MM-DD by Stellan · Status: active / reversed (link to the replacement)
## Context · ## Options considered · ## Decision & why · ## Revisit when
```

### 4.5 Daily page (`wiki/daily/daily-YYYY-MM-DD.md`)
```markdown
# <Weekday> YYYY-MM-DD
> Energy AM n/10 · PM n/10 · Raw: `raw/daily/…`

## Morning
- **Top 3:** 1. … 2. … 3. …
- **FlowPilot today:** …
- **Apprentice today:** …
- **On my mind:** …

## Evening
- **Done:** ✅ / ⏳ against each Top 3 item
- **FlowPilot:** wins, client/lead updates, numbers
- **Apprentice:** progress, bugs, decisions, market notes
- **Learned / ideas:** …
- **Tomorrow first:** …

## Filed to
- [[page]]: what was added
```

### 4.6 Citations
- A fact from a source cites the source page: `([[src-slug]])`.
- Something Stellan said in chat or a check-in: `*(Stellan, YYYY-MM-DD)*`, or link the daily page `([[daily-YYYY-MM-DD]])`.
- Claude's own inference: `*(synthesis)*`. General knowledge: `*(general knowledge)*`. Not sure: `*(unverified)*`.
- Never state something as fact without one of these.

---

## 5. Special files

### 5.1 `wiki/index.md`
- Every wiki page, grouped as: **Home**, **Investing Apprentice**, **FlowPilot**, **Daily**, **Sources**.
- One line per page: `- [[slug]]: one-line summary · <metadata>`. Entity/concept pages end with
  `· N sources`. Daily pages are newest first and list only the last 14 days (the full list is on
  [[daily-run-through]]). Sources are newest first. Everything else is alphabetical.
- Update it on every operation that creates, renames, or deletes a page, or changes what a page is about.

### 5.2 `wiki/log.md`
- Append-only, newest at the bottom. Every entry starts with `## [YYYY-MM-DD] <op> | <subject>`,
  where `<op>` ∈ `setup | ingest | query | lint | schema | edit | morning | evening`.
- Body bullets: read, `+` created, `~` updated, `-` deleted, `⚠️` contradiction, `→` follow-up.
- Recent activity: `grep "^## \[" wiki/log.md | tail -5`

### 5.3 `wiki/overview.md` (Home)
- The big picture across all three sections: what Stellan is working on, how the sections connect,
  this week's focus, and top open loops. Rewrite it; don't just append.

---

## 6. Workflows

### 6.1 MORNING CHECK-IN
Triggers: "morning", "gm", "check-in", "start my day", or the first message of a day that isn't
about something else.
1. Read [[daily-run-through]] (open loops), yesterday's daily page (its "Tomorrow first" item), and both section hubs' Snapshots and Open questions.
2. Ask the **morning questions** from [[daily-run-through]] in one short message. Add **at most one**
   open question from a hub, and mention yesterday's carry-overs by name.
3. When Stellan answers, capture the answers verbatim in `raw/daily/YYYY-MM-DD-morning.md`.
4. Create `wiki/daily/daily-YYYY-MM-DD.md` and fill in its Morning section.
5. Reply with a short **day plan**: the Top 3 in order, with anything due in FlowPilot or the Apprentice next to the right item.
6. File new facts into the section pages (§6.3 step 6), update the index, log a `morning` entry, and commit.

### 6.2 END-OF-DAY REVIEW
Triggers: "eod", "end of day", "evening", "wrap up", "review my day".
1. Read today's daily page.
2. Ask the **evening questions** in one short message. Name the morning's Top 3 so Stellan can tick them off.
3. Capture the answers verbatim in `raw/daily/YYYY-MM-DD-evening.md`. Fill in the Evening section.
4. **File everything:** client and lead updates go to FlowPilot pages, product progress and decisions
   to Apprentice pages, and ideas to the right hub. Update each hub's Snapshot when the state changed.
   List every page touched under "Filed to".
5. Carry unfinished items to Open loops on [[daily-run-through]]. Remove loops that are closed.
6. Reply with a 3-line recap: what moved, what's open, and the first task for tomorrow.
7. Update the index and overview if this week's focus changed, log an `evening` entry, and commit.

### 6.3 INGEST (Stellan drops a file in `raw/…`, pastes a source, or says "ingest X")
1. Locate the file, or capture the paste into the right `raw/` subfolder (§4.1).
2. Read all of it. 3. Read the index and the pages it touches.
4. **Discuss:** 3–7 takeaways, the pages to create or update, and any contradictions. Ask what to emphasize.
   *(Skip this only if Stellan says "just do it" or "batch", and write "unsupervised" in the log entry.)*
5. Write `wiki/sources/src-<slug>.md` (TL;DR · Key points · Notable quotes · How it connects · Pages touched).
6. Update or create section pages. Integrate facts *into* existing text, cite them, and flag contradictions
   on **both** pages. Keep the section hub's "Pages" list and Snapshot current.
7. Update the overview, the index, and the log. Commit as `ingest: <title>`. Report back with 1–3 follow-ups.

### 6.4 QUERY (any question about Stellan's work, product, business, or days)
1. Read the index first, then the relevant pages. Use `python3 tools/wiki.py search "<terms>"` when the index alone doesn't make it obvious which pages matter.
2. Answer with citations. Say clearly what the brain doesn't know yet, and label general knowledge.
3. Pick the format that fits: prose, a table, a chart, or slides.
4. **File back** answers worth keeping as an analysis or decision page in the right section, linked from its hub.
5. Log a `query` entry, and commit if files changed.

### 6.5 LINT ("lint", "health check"; Claude may suggest one weekly)
Run `python3 tools/wiki.py lint` first. It checks broken links, orphans, index drift, frontmatter,
and raw files that haven't been processed. Then do the judgment checks:
- Contradictions and stale claims, especially old numbers and statuses
- Hub Snapshots that disagree with recent daily pages
- Open loops older than 7 days
- Hub open questions that a check-in could answer
Fix mechanical issues directly. Bring judgment calls to Stellan. Log a `lint` entry and commit.

### 6.6 EDIT (Stellan asks for a specific change)
Make the change, keep links, the index, and frontmatter consistent, log an `edit` entry, and commit.

### 6.7 AGENTS & THE APP INBOX
- Stellan adds links and notes in the app. They land in the app database's `inbox`.
- **Brain · Inbox agent** (every 2 h, 6:53–22:53 Toronto) and **Brain · Morning brief** (daily 6:18,
  email ~6:30 to rowbs34@gmail.com) are claude.ai Routines. Each starts a fresh session that follows
  `agents/protocol.md`, then `agents/inbox-agent.md` or `agents/morning-brief.md`.
- Agent runs are ingests done unsupervised. They follow §6.3 and log `ingest` entries noting "agent run".
- In chat, when Stellan pastes a link, Claude can handle it directly (as an ingest), or add it to the inbox when Stellan says "queue it".
- Any session that changes the hubs refreshes the app's `brain/snapshot` so the app stays in sync.
- To change agent behaviour, edit the file in `agents/` and log a `schema` entry.

---

## 7. Writing style & guardrails

- Clear, plain, and neutral. Lead with the most important point. Use bullets for facts and short prose for reasoning.
- Keep pages focused. Split a page once it covers two things or passes ~800 words.
- Use absolute dates (`2026-10-10`), never relative ones.
- **Personal material** (check-ins, energy, worries) stays factual and non-judgmental, and never goes to
  an external service.
- **Investing:** the Apprentice section records product work and market research. Every price, return,
  or market figure carries its date and source. Claude does not invent figures, and does not present
  buy or sell calls as fact. Strategy notes describe how a strategy works and its known risks.
- **Business:** client names and money figures stay in this private repo, and are never sent to outside tools without Stellan's OK.

---

## 8. Asking questions

When something is unclear, ask, the way Stellan asked to be asked. Prefer one short question to
guessing. Anything still unknown goes under the relevant hub's **Open questions**, and the morning
check-in works through them one at a time.

---

## 9. Git conventions

- One commit per operation, with the message `<op>: <subject>` (e.g. `evening: 2026-10-10`, `ingest: Client brief – Acme`).
- Push to the working branch after committing.

---

## 10. Schema evolution

- Co-owned: Claude proposes a change, Stellan approves it, Claude edits this file and logs a `schema` entry.
- Changelog:
  - 2026-10-01: v1. Generic LLM Wiki schema based on Karpathy's idea file.
  - 2026-10-02: v1.1. Added `tools/wiki.py` and the lint-before-finishing rule.
  - 2026-10-10: **v2. Became Stellan's Brain.** Demo pages deleted (they're still in git history at
    `b76fec2`). Three sections (Investing Apprentice, FlowPilot with ACE, Daily Run-Through), new
    `hub` and `daily` page types, morning and evening workflows, and investing and business guardrails.
  - 2026-10-10: **v2.1. The live app and agents.** Added the app (link inbox, agent status, schedule,
    morning breakdown), `agents/` instructions, two Routines (inbox every 2 h, 6:30 AM email),
    the `wiki/daily/schedule.md` page, research pages (`kind: asset`), and §6.7.

---

## 11. Every interaction checklist

Decide which operation it is: **morning / evening / ingest / query / lint / edit / schema / chit-chat**.
For anything except chit-chat, before the turn ends:
- [ ] existing `raw/` files are untouched (new captures are fine)
- [ ] new and changed pages have correct frontmatter, citations, and links, and are listed on their hub
- [ ] `index.md` and the hub Snapshots reflect the current state
- [ ] `log.md` has a new entry at the bottom
- [ ] `python3 tools/wiki.py lint` is clean (or only shows deliberate red links)
- [ ] changes are committed and pushed
