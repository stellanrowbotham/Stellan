---
type: overview
title: Overview
aliases: ["Second brain overview", "Synthesis"]
tags: [meta]
created: 2026-10-01
updated: 2026-10-10
sources: [src-agent-roster-2026-10-10, src-stellan-investing-apprentice-brief]
---

# Overview
The top-level synthesis of Stellan's second brain. It is rewritten (not appended to) as understanding changes. The wiki was reset on 2026-10-10 and now has two sections.

## 1. My agents
Stellan runs a small team of AI agents. They all report to one live dashboard, [[stellans-brain]] ([[src-agent-roster-2026-10-10]]).
- **Daily life team (scheduled):** [[morning-rundown]] (7:45 AM), [[inbox-sweep]] (six times a day) and [[six-pm-update]] (5:51 PM). They read email and calendars, propose calendar adds, draft replies, and never send or delete anything themselves.
- **Business team:** [[ace]] does outreach on request, and [[flowpilot]] answers website inquiries automatically.
- **Investing:** the [[investing-apprentice]], built 2026-10-10. It is at Level 1 and waiting on data access.
- Around-the-clock view: [[agents-24-7]].

**Pattern so far:** agents are allowed to *read and propose* but not to *act* on anything that can't be undone. Stellan stays the one who approves *(synthesis)*. The investing apprentice extends that pattern: it trades only pretend money, and code enforces its limits ([[src-stellan-investing-apprentice-brief]]).

## 2. Investing knowledge
Starting point: learn how markets work by watching an AI apprentice research, predict and paper-trade with $1,000 CAD of pretend money, with every decision recorded before the outcome is known ([[src-stellan-investing-apprentice-brief]]).
- Core ideas so far: [[paper-trading]], [[look-ahead-bias]], [[trading-costs]], [[risk-management]], [[promotion-system]] and [[source-reliability]].
- **Evolving thesis:** honest records beat clever predictions. A strategy only "works" if it still beats a simple benchmark after costs, on data it never saw while being designed *(synthesis)*.

## Open questions / gaps
- [[investing-apprentice]] can't research yet. It needs the data sites allowed in the cloud environment's network settings, free API keys, and Gmail added to its Routines (`apprentice/README.md`).
- Do free data plans cover TSX prices? This will show on the first run with keys ([[source-reliability]]).
- Questrade's official fee schedule still needs checking ([[trading-costs]]).
- [[flowpilot]]: is the n8n workflow still active after the trial pause? The n8n connector needs fixing.
- [[ace]]: its instructions haven't been captured yet.
- School email isn't connected to the hub yet ([[morning-rundown]]).
