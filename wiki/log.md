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

## [2026-10-10] edit | Apprentice moved to Level 2 with a 4-hourly opportunity scan
- Stellan: "every 4 hours look for a new stock to buy … fake buy … I am training you not me"
- Config level 1 → 2 (re-approved hash); promotion recorded in `level_events`; crypto Routine turned into "Opportunity scan" every 4 h and switched on
- ~ [[investing-apprentice]], [[promotion-system]], [[agents-24-7]], [[investing-apprentice-plan]], [[overview]], [[index]]
- ⚠️ Level 1's forecast check was skipped by choice; still blocked on network access, keys and Gmail

## [2026-10-11] edit | Apprentice test run and runner session
- Test: the fresh-session Routines couldn't reach the repo or Gmail. Replaced them with 4 Routines bound to one runner session (`apprentice/ROUTINES.md`)
- Live data now flowing: Bank of Canada, Kraken (BTC, ETH, SOL, XRP, DOGE in CAD), CoinGecko, DefiLlama, Alpha Vantage, 7 news feeds
- ⚠️ Twelve Data and Finnhub return 401 and FRED returns 400, meaning those keys are rejected by the providers; Stellan to re-enter them
- ~ [[investing-apprentice]], [[agents-24-7]]

## [2026-10-12] edit | Levels turned off; first-weekend fixes
- Stellan: "have the agent make these fake trades and actually make or lose money and drop the level thing"
- Config: levels off, demotions off, minimum candidate score 65 → 55; guide now requires buying any candidate that passes
- Fixed: a shadowed `time` import (from the 2026-10-11 Alpha Vantage throttle) crashed every stock collection; regression test added
- ~ [[investing-apprentice]], [[promotion-system]], [[investing-apprentice-plan]], [[overview]], [[index]]
- ⚠️ Twelve Data and Finnhub keys still return 401, and the FRED key still returns 400

## [2026-10-12] edit | Trade rules loosened
- Stellan chose "Loosen a bit": minimum candidate score 55 → 45, reward:risk 2.0 → 1.5
- Fixed: the live price record now counts as licensed evidence when scoring (crypto candidates wrongly failed the "official/licensed source" gate)
- ~ [[investing-apprentice]] behaviour only; risk limits unchanged
