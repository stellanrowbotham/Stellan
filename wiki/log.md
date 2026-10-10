---
type: meta
section: brain
title: Log
tags: [meta]
created: 2026-10-10
---

# Log
Append-only, newest at the bottom. Each entry starts with `## [YYYY-MM-DD] op | subject`.
Last 5 entries: `grep "^## \[" wiki/log.md | tail -5`
The log from the earlier LLM Wiki demo (2026-10-01 to 2026-10-02) is in git history at commit `b76fec2`.

## [2026-10-10] schema | v2: LLM Wiki becomes Stellan's Brain
- Stellan asked to clear the LLM Wiki demo and restructure it into three sections. Answers to clarifying questions: FlowPilot is the business, and ACE is Stellan's business assistant in Claude chats. The Apprentice is a product Stellan is building. The daily run-through is a morning check-in plus an end-of-day review. The old pages should be deleted.
- \- deleted the 15 demo pages (sources, entities, concepts, analyses) and 3 raw files (Karpathy idea file, qmd README, qmd code excerpts)
- ~ `CLAUDE.md` rewritten as v2: sections, `hub` and `daily` page types, morning and evening workflows, investing and business guardrails
- ~ `tools/wiki.py`: new page types, plus support for daily pages that link several raw files
- + [[investing-apprentice]], [[flowpilot]], [[ace]], [[daily-run-through]]
- ~ [[overview]] rewritten as the Stellan's Brain home page; [[index]] regrouped by section
- → The first morning check-in fills in the hubs' Open questions, one at a time

## [2026-10-10] schema | v2.1: live app, agents, and the daily email
- Stellan asked for an app showing the brain, daily emails, live agent activity, and a place to drop links (for example a hockey schedule to add to the calendar, or a stock to research). Answers to clarifying questions: email goes to rowbs34@gmail.com at 6:30 AM Toronto time, agents run every 2 h from 7am to 11pm, and schedule links go into Google Calendar as well as the brain.
- + App published: https://claude.ai/artifact/RmkjrydKPNeqMoYjDdNXm5 (private database, readable and writable only by the owner and editors)
- + `agents/README.md`, `agents/protocol.md`, `agents/inbox-agent.md`, `agents/morning-brief.md`
- + [[schedule]]
- ~ `CLAUDE.md` §0/§2/§3/§4/§6.7/§10, [[overview]], [[daily-run-through]], [[index]]
- ⚠️ The cloud environment blocks most websites (nhl.com, finance.yahoo.com, wikipedia.org tested). Web search works. Until network access is widened, agents fall back to search and mark links they can't open as "Needs you".
- → Routines: Brain · Inbox agent and Brain · Morning brief
