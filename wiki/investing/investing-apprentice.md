---
type: hub
section: investing
title: AI Stock & Crypto Investing Apprentice
aliases: ["Investing Apprentice", "Apprentice", "AI Investing Apprentice"]
tags: [product, investing, stocks, crypto, ai, simulation]
created: 2026-10-10
updated: 2026-10-10
sources: [src-command-centre]
---

# AI Stock & Crypto Investing Apprentice
An AI agent Stellan is building that researches stocks and crypto, makes forecasts, and paper-trades with virtual money. It earns promotions as it proves itself *(Stellan, 2026-10-10)* ([[src-command-centre]]).

## Snapshot
- **What it is:** a research-and-forecasting agent for TSX/US stocks and crypto that paper-trades $1,000 CAD of virtual money. Simulation only: there is no code for real-money trading. ([[src-command-centre]])
- **Stage:** set up 2026-10-10 at **Level 1 (Research Apprentice)**. ([[src-command-centre]])
- **Blocker:** every data source is blocked by the cloud network settings or needs a free API key, so it hasn't produced research yet. ([[src-command-centre]])
- **Dashboard:** its own private app (Overview, Research, Paper trading, Learning, Progress, Settings). See [[connected-apps]].

## Vision
An apprentice that has to *earn* trust. It starts by writing research and forecasts, gets scored on accuracy and calibration, and moves up a ladder only when it meets every requirement and Stellan approves. Even the top level never unlocks real money. ([[src-command-centre]])

## Target user
Stellan, for now *(synthesis)*. Whether it becomes a product for others is an open question.

## Features
| Feature | Status | Source |
|---|---|---|
| Pre-market research report (weekdays 8:27 AM) and after-the-bell update (4:33 PM) | Built; waiting on data | [[src-command-centre]] |
| Crypto checks every 4 h and an hourly experiment | Paused until data is connected | [[src-command-centre]] |
| Forecasts scored for hit rate and Brier score, with a calibration table | Built | [[src-command-centre]] |
| Paper trading with fees and slippage, stop-loss required, long only | Unlocks at Level 2 | [[src-command-centre]] |
| 5-level promotion ladder, scorecard of rewards and penalties, and demotions | Built | [[src-command-centre]] |
| Mistake journal, lessons and post-trade reviews | Built | [[src-command-centre]] |
| Risk limits: position, sector and crypto caps, daily-loss halt, drawdown review | Built | [[src-command-centre]] |
| Stellan approves settings changes and promotions | Built | [[src-command-centre]] |
| This brain's Stock Agent researching any ticker dropped in the app | Built (uses web search) | `agents/inbox-agent.md` |

## Tech & data stack
- Runs as scheduled Claude agents. Its results are written to the dashboard's database. ([[src-command-centre]])
- **Data:** market data and news feeds are currently blocked or need free API keys. ([[src-command-centre]])

## Roadmap
1. Connect data: allow the sources in the cloud environment's network settings, or add free API keys.
2. First research reports and scored forecasts at Level 1.
3. Earn Level 2, which unlocks paper trading with Stellan's approval.

## Decisions
*(None recorded as decision pages yet.)*

## Research
- **Markets & assets:** TSX and US stocks, plus crypto ([[src-command-centre]])
- **Stock Agent research:** *(none yet. Drop a ticker link in the app.)*
- **Competitors:** *(none yet)*

## Open questions
1. Which free API keys should the Apprentice get (market data, news)?
2. Should it stay your own research tool, or become a product for other people?
3. How should the Stock Agent's research (from links you drop) feed the Apprentice's reports?

## Pages
- Sources: [[src-command-centre]]
- Related: [[connected-apps]] · [[flowpilot]] · [[daily-run-through]] · [[overview]]
