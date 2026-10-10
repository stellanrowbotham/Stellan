---
type: agent
kind: routine
title: Investing Apprentice
aliases: ["AI investing apprentice", "Stock and crypto apprentice", "Apprentice"]
tags: [agents, investing]
status: live (Level 1, data blocked)
schedule: 8:27 AM and 4:33 PM weekdays; crypto every 4 h and hourly experiment paused
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Investing Apprentice
A planned AI agent that studies Canadian and US stocks and crypto, makes **pretend** trades with pretend money, keeps an honest record of how they turn out, and earns promotions by proving it's careful and right more often than chance.

## In plain words
Picture a new employee at an investing company. On day one they can't touch any money. First they read the news, make predictions and write down *why*. If those notes are honest and well sourced, they're allowed to trade with play money. Every trade is written down before it happens, so it can't be changed afterwards. When a trade ends, they ask "was I right, or just lucky?" Only steady, careful results over many months earn a promotion, and even the top level never gets real money on its own *(synthesis)*.

## Key facts
- Status: **built and scheduled on 2026-10-10, Level 1** (forecasts only). Plan approved by Stellan the same day; see [[investing-apprentice-plan]] *(Stellan, 2026-10-10)*.
- ⚠️ **Can't research yet:** on its first run every data site was blocked by the cloud environment's network policy, and the free API keys aren't set. The fix is in `apprentice/README.md` → Setup *(synthesis)*.
- Dashboard (private, works on phone): [Investing Apprentice](https://claude.ai/artifact/PHFxL9AAwnp1DRxWzXLMUQ). Also shown as an agent card on [[stellans-brain]].
- Code: `apprentice/` in this repo; 56 automated tests; append-only, hash-chained records, so old predictions can't be quietly edited *(synthesis)*.
- Routines: Pre-market `trig_01EBzV8jv969JgHxMPNSrwjt` and After the close `trig_01A5A8LVVor9ofNUqa4tYF5z` are on. Crypto check `trig_01EZPKbyn9wamX7f7gvKEtpi` and Hourly experiment `trig_01CXcNa8V3PhuiNXPq17hKxY` are paused until data works. They have no Gmail connector yet, so email won't send until Stellan adds it.
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
