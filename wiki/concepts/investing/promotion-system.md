---
type: concept
title: Promotion system (agent levels)
aliases: ["Agent levels", "Apprentice levels", "Scorecard", "Rewards and penalties"]
tags: [investing, agents]
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Promotion system (agent levels)
How the [[investing-apprentice]] earns more responsibility. It moves up by proving it's careful and honest over time, not by getting lucky.

## In plain words
Like belts in karate: you can't skip to black belt by winning one fight. You need to show good form many times, and you can be sent back a level if you get sloppy *(synthesis)*.

## Explanation
| Level | Can do | To move up *(proposed defaults, configurable)* |
|---|---|---|
| 1 Research Apprentice | Research and predictions only, no trades | 20 trading days, 50 recorded forecasts, zero made-up data or timestamp errors |
| 2 Paper-Trading Apprentice | Pretend trades and reviews | 60 days, 30 closed trades, every risk rule followed, every review complete |
| 3 Research Analyst | Compare strategies, deeper reports | 6 months; beats its benchmark after costs on a held-out period; no single trade above 25% of profits; drawdown under 15% |
| 4 Senior Analyst | Bigger simulated limits, strategy monitoring | 12 months across at least 2 different market conditions |
| 5 Trusted Research Agent | Independently evaluated research | Doesn't unlock real money, ever, by itself |

The levels come from [[src-stellan-investing-apprentice-brief]]. The numbers are Claude's proposed defaults, accepted on 2026-10-10 *(Stellan, 2026-10-10)*.

- Every promotion that changes permissions needs Stellan's approval ([[src-stellan-investing-apprentice-brief]]).
- The scorecard rewards discipline, accurate records and risk control. More trades, more research or more confident predictions don't automatically earn points ([[src-stellan-investing-apprentice-brief]]).
- Penalties apply for made-up facts, broken risk rules and integrity violations, and the agent can be demoted ([[src-stellan-investing-apprentice-brief]]).
- **Benchmarks** (what "beating the market" means), proposed for a Canadian focus: XIU (the TSX 60 fund) for Canadian stocks, SPY converted to CAD for US stocks, and Bitcoin in CAD for crypto *(synthesis)*.

## Evidence & claims
- The agent must never be promoted solely because of a high short-term return ([[src-stellan-investing-apprentice-brief]]).

## Tensions & contradictions
- ⚠️ With $1,000 and a 10% position limit, Level 2's 30 closed trades could take several months. Status: open. The threshold might need lowering, or the observation period counted in trades rather than days *(synthesis)*.

## Related
- [[risk-management]], [[paper-trading]]
