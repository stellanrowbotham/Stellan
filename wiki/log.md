---
type: meta
title: Log
tags: [meta]
created: 2026-10-01
---

# Log
Append-only. Newest entries at the bottom. Each entry starts with `## [YYYY-MM-DD] op | subject`.
Last 5 entries: `grep "^## \[" wiki/log.md | tail -5`

> The log before 2026-10-10 was cleared together with the rest of the wiki at Stellan's request. It is preserved in git history (commit `b76fec2` and earlier).

## [2026-10-10] schema | v1.2: wiki reset, new Agents and Investing sections
- Stellan asked to delete everything in `wiki/` and `raw/` and start fresh. Removed 16 wiki pages and 3 raw files (the LLM Wiki / qmd material), which are recoverable from git history
- + `wiki/agents/` (new top-level folder, `type: agent`), `wiki/concepts/investing/` (subfolder)
- ~ `CLAUDE.md` §2, §4.6 (agent template, citations moved to §4.7), §5.1, §9; ~ `tools/wiki.py` (agent type)

## [2026-10-10] ingest | Agent roster snapshot
- Read: Routine settings (3 Routines) and the Brain `agents` collection (5 docs). Captured as `raw/2026-10-10-agent-roster-snapshot.md` with email addresses redacted
- Mode: unsupervised (Stellan: "add the agents and make a page for each agent")
- + [[src-agent-roster-2026-10-10]], [[stellans-brain]], [[morning-rundown]], [[inbox-sweep]], [[six-pm-update]], [[ace]], [[flowpilot]], [[agents-24-7]]
- ⚠️ [[flowpilot]] unchecked since 2026-09-30, because the n8n connector fails (also in this session)
- → Paste Ace's instructions so [[ace]] can be documented fully

## [2026-10-10] ingest | Stellan's investing apprentice brief
- Read: `raw/2026-10-10-investing-apprentice-brief.md` (captured from Stellan's paste), plus interview answers given in chat
- + [[src-stellan-investing-apprentice-brief]], [[investing-apprentice]], [[investing-apprentice-plan]]
- + [[paper-trading]], [[look-ahead-bias]], [[trading-costs]], [[risk-management]], [[promotion-system]], [[source-reliability]]
- ⚠️ Free-plan TSX price coverage unconfirmed, which conflicts with the Canadian-first goal; secondary sources disagree on the crypto spread
- → Plan awaiting approval; Phase 1 verifies each data source's terms and limits

## [2026-10-10] edit | Investing Apprentice built and scheduled
- Stellan approved the plan. Decisions: email to his own address only, day trading as a labelled hourly experiment, Questrade fee model
- Built `apprentice/` (engine, 56 tests, CI workflow), dashboard https://claude.ai/artifact/PHFxL9AAwnp1DRxWzXLMUQ, 4 Routines (2 on, 2 paused), and an agent card plus log line on the Brain
- ~ [[investing-apprentice]], [[investing-apprentice-plan]], [[agents-24-7]], [[stellans-brain]], [[trading-costs]], [[overview]], [[index]]
- ⚠️ First real run: every data host was blocked by the network policy and no API keys are set. The Routines have no Gmail connector
- → Stellan: allow the domains, add the free keys, and add Gmail to the Routines (see `apprentice/README.md`); then turn on the crypto and hourly Routines
