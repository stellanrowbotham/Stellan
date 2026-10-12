---
type: agent
kind: routine
title: Investing Apprentice
aliases: ["AI investing apprentice", "Stock and crypto apprentice", "Apprentice"]
tags: [agents, investing]
status: live (levels off, everything unlocked)
schedule: 8:27 AM and 4:33 PM weekdays; opportunity scan every 4 h; hourly experiment paused
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Investing Apprentice
A planned AI agent that studies Canadian and US stocks and crypto, makes **pretend** trades with pretend money, keeps an honest record of how they turn out, and earns promotions by proving it's careful and right more often than chance.

## In plain words
Picture a new employee at an investing company. On day one they can't touch any money. First they read the news, make predictions and write down *why*. If those notes are honest and well sourced, they're allowed to trade with play money. Every trade is written down before it happens, so it can't be changed afterwards. When a trade ends, they ask "was I right, or just lucky?" Only steady, careful results over many months earn a promotion, and even the top level never gets real money on its own *(synthesis)*.

## Key facts
- Status: **built and scheduled on 2026-10-10.** Stellan moved it straight to **Level 2 (pretend trading)** the same day, skipping the forecast-only Level 1: "I am training you not me" *(Stellan, 2026-10-10)*.
- **Levels turned off on 2026-10-12**: everything simulated is unlocked, with no promotions or demotions. Risk limits still apply, and a candidate that passes every check must be bought (minimum score lowered from 65 to 55) *(Stellan, 2026-10-12)*.
- First live weekend (2026-10-10 to 2026-10-12): 0 trades. A code bug crashed stock collection, the Twelve Data, Finnhub and FRED keys were rejected, and the one Solana candidate that passed (2026-10-12 10:33 AM) wasn't proposed. All three are fixed or reported *(synthesis)*.
- **Every 4 hours** it hunts for a new stock or crypto to buy, and pretend-buys up to 2 when they pass every check *(Stellan, 2026-10-10)*.
- Original Level 1 start: Plan approved by Stellan the same day; see [[investing-apprentice-plan]] *(Stellan, 2026-10-10)*.
- ⚠️ **Can't research yet:** on its first run every data site was blocked by the cloud environment's network policy, and the free API keys aren't set. The fix is in `apprentice/README.md` → Setup *(synthesis)*.
- Dashboard (private, works on phone): [Investing Apprentice](https://claude.ai/artifact/PHFxL9AAwnp1DRxWzXLMUQ). Also shown as an agent card on [[stellans-brain]].
- Code: `apprentice/` in this repo; 56 automated tests; append-only, hash-chained records, so old predictions can't be quietly edited *(synthesis)*.
- Routines: Since 2026-10-11 all four (Opportunity scan `trig_01QKsnz2SDFE8aPVmfpd7MHK`, Pre-market `trig_01FmUM5ztD9juXXFidRQtDhh`, After the close `trig_01U9PAFTabbCKbruyu8eodNT`, Hourly experiment `trig_01AjwVsVAvt7u9R36KUW7PCK`) run inside one runner session that has the code and Gmail. The first versions couldn't reach the repo, so they were replaced (`apprentice/ROUTINES.md`).
- Simulation only. It has no ability to place real orders ([[src-stellan-investing-apprentice-brief]]).
- Starting virtual balance: **$1,000 CAD**, with a Canadian focus (TSX first, then US) *(Stellan, 2026-10-10)*.
- Five levels, from Research Apprentice to Trusted Research Agent ([[promotion-system]], [[src-stellan-investing-apprentice-brief]]).
- Trading style: try everything, with individual trades, and learning first before trading for real results *(Stellan, 2026-10-10)*.
- Reports go by email, **only to Stellan's own address**, and explain things simply, the way you would to a 10-year-old *(Stellan, 2026-10-10)*.
- Fees are modelled on **Questrade** (his likely future broker) for stocks and Kraken for crypto ([[trading-costs]]) *(Stellan, 2026-10-10)*.
- Day trading runs only as a **labelled hourly experiment** *(Stellan, 2026-10-10)*.

## How it fits with the other agents
- Runs as Claude Routines, like [[morning-rundown]] and the others, and reports to its own dashboard plus a card and log lines on [[stellans-brain]] *(synthesis)*.
- The [[six-pm-update]] health check now sees its card and will flag missed runs *(synthesis)*.
- It will be the only agent working overnight, because crypto trades 24/7. See [[agents-24-7]].

## Related
- [[paper-trading]], [[look-ahead-bias]], [[trading-costs]], [[risk-management]], [[source-reliability]]
