---
type: analysis
title: Investing Apprentice: requirements and build plan
aliases: ["Apprentice plan", "Investing agent plan"]
tags: [investing, agents, plan]
question: What exactly should the Investing Apprentice be, and how should it be built?
status: approved 2026-10-10; phases 1-2 built
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Investing Apprentice: requirements and build plan
> Filed from the interview on 2026-10-10. **Approved by Stellan on 2026-10-10** *(Stellan, 2026-10-10)*. Phases 1-2 were built the same day, and the engine for phases 3-4 is in place and tested; see [[investing-apprentice]].

## 1. What Stellan wants (interview answers, 2026-10-10)
| Topic | Answer |
|---|---|
| Goal | All three (learn, understand markets, simulated returns). Learning first, then trading for real results |
| Markets | TSX and US (NYSE/Nasdaq) only. Stay on the Canadian side where possible |
| Universe | Starter universe (S&P/TSX 60, S&P 500, about 20 ETFs, top 20 crypto), narrowed by the agent into a watchlist |
| Currency | CAD is the home currency; US trades pay the FX fee |
| Style | "Try everything": swing, long-term and day-trading experiments, each scored separately |
| Money | $1,000 CAD virtual. Individual trades, not a managed portfolio |
| Explanations | Like explaining to a 10-year-old |
| Schedule | 8:30 AM pre-market, 4:30 PM after-close, crypto every 4 hours |
| Alerts | Email |
| Budget | $0/month, free data plans |
| Dashboard | Private, and must work on the phone |
| Runs on | Claude Routines (like [[morning-rundown]] and the others) |
| AI | Claude |
| Risk limits, promotions, benchmarks | Defaults accepted ([[risk-management]], [[promotion-system]]) |

All answers are *(Stellan, 2026-10-10)*. The full brief is in [[src-stellan-investing-apprentice-brief]].

## 2. Version 1 vs later
**V1:** the source registry; free data adapters; a validated, timestamped data store; the daily email report with ranked candidates or "No trade"; Level 1 (forecasts only), then Level 2 paper trading; realistic CAD costs; a TSX/NYSE market calendar; the risk engine; append-only records; post-trade reviews; a promotion evaluator; a phone-friendly dashboard; tests.
**Later:** walk-forward strategy experiments, Level 3+ evaluation, more data providers, CSV export of everything, and anything involving a real brokerage. Live trading is not in scope at all.

## 3. Technology (recommended)
- **Engine:** Python package in this repo (`apprentice/`). Plain code does the maths that must be exact: accounting, costs, risk limits, promotion scores. Claude does the reading, reasoning and writing *(synthesis)*.
- **Where it runs:** Claude Routines, each firing a fresh session that checks out this repo, runs the engine, and commits the new records *(synthesis)*.
- **Storage:** append-only JSON-lines files (forecasts, trades, price snapshots, reviews, scorecard), each record hash-chained to the one before. Old predictions physically can't be edited without the chain breaking, and git history is a second audit trail *(synthesis)*.
- **Dashboard:** a private claude.ai artifact, like [[stellans-brain]]. It works on the phone and needs no server, and is linked from the Brain *(synthesis)*.
- **Email:** sent through the connected Gmail, **only to Stellan's own address** *(Stellan, 2026-10-10)*.
- **Free data, first choice:** Bank of Canada Valet (CAD rates, USD/CAD), Statistics Canada, FRED, SEC EDGAR, CoinGecko (free key), Kraken public market data (real crypto bid/ask), DefiLlama, Twelve Data / Alpha Vantage / Finnhub free keys for stock prices, and RSS headlines from the news outlets *(general knowledge, each to verify before use)*.

## 4. Costs and limits
- Data: $0 on free plans. The catch is limits: about 25 calls a day on Alpha Vantage and 800 on Twelve Data, free prices are often delayed up to 15 minutes, and **TSX coverage on free plans is unconfirmed** *(unverified, web search 2026-10-10)*.
- AI: Routine runs use Stellan's Claude plan. There is no separate bill, but it counts toward usage limits *(synthesis)*.
- **Day trading is limited.** Routines run at most about hourly and free prices are delayed, so real day trading can't be simulated honestly. Proposal: day trading becomes a clearly labelled "experiment" scored only on hourly prices, or it waits until paid real-time data *(synthesis)*.
- Maintenance: free APIs change terms. The registry marks broken sources, and the 6 PM health check can include the apprentice *(synthesis)*.

## 5. Architecture
```
sources registry ─► collectors ─► validator/timestamper ─► snapshot store (append-only)
                                                         │
                     Claude research (Routine) ◄─────────┘
                                │ proposes
                                ▼
               risk engine (code, read-only limits) ──► paper broker (sim only, no live code)
                                │                                │
                         journal + reviews ◄──── portfolio accounting
                                │
                 scorecard + promotion evaluator (code)
                                │
                  dashboard sync + email report
```
Live trading would be a separate module that doesn't exist. The paper broker has no network code that could place a real order *(synthesis)*.

## 6. Phases
1. **Foundation:** repo skeleton, config, source registry (all 45 entries checked for access), hash-chained store, market calendar, tests.
2. **Research (Level 1):** data adapters, validation, the daily email report with forecasts only, the Routines, and a v1 dashboard.
3. **Paper trading (Level 2):** simulator, costs, risk engine, accounting, post-trade reviews.
4. **Learning and promotions:** scorecard, evaluator, strategy library, experiments waiting for approval.
5. **Polish:** full dashboard tabs, exports, monitoring and alerts.

## 7. How success is measured
- **Simulation accuracy:** accounting must reconcile on every run (cash + positions = value). Every fill is checked against a stored real quote.
- **Learning:** forecast hit-rate and calibration (did 70%-confident calls come true about 70% of the time?), compared before and after each approved change.
- **Promotions:** only the coded criteria in [[promotion-system]], with a written pass/fail reason for each one.

## 8. Security and safeguards
- No brokerage connection and no brokerage credentials.
- API keys go in the Routine environment's secrets, never in the repo, reports or the dashboard.
- Risk limits and promotion rules live in a config file the agent is told never to edit, and a test fails if they change without a matching approved-config hash *(synthesis)*.
- Emails, news and web pages are treated as information, never instructions. This is the same rule as the existing agents ([[src-stellan-investing-apprentice-brief]]).

## 9. Decisions (2026-10-10)
1. Plan: **approved**.
2. Email: **send to Stellan's own address only**.
3. Day trading: **labelled hourly experiment**.
4. Fee model: **Questrade** for stocks *(Stellan, 2026-10-10)*.

## 10. What's still blocking (as of 2026-10-10)
- The cloud environment's network policy blocks every data host, from the first run *(synthesis)*.
- Free API keys aren't set (Twelve Data, Alpha Vantage, Finnhub, FRED, CoinGecko, SEC user agent).
- The Routines have no Gmail connector, because they were created from a session that couldn't pass connectors.
- Steps for all three are in `apprentice/README.md` and `apprentice/ROUTINES.md`.

## Basis
- Pages used: [[src-stellan-investing-apprentice-brief]], [[risk-management]], [[promotion-system]], [[trading-costs]], [[source-reliability]], [[agents-24-7]]
