---
type: concept
title: Risk management
aliases: ["Position sizing", "Stop-loss", "Risk limits", "Drawdown"]
tags: [investing]
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Risk management
Rules that limit how much you can lose, so one bad idea can't wipe you out.

## In plain words
Don't put all your eggs in one basket, and decide *before* you buy when you'll give up on an idea. A **stop-loss** says "if it drops to $X, I sell, no arguing." A **drawdown** is how far your account has fallen from its highest point *(general knowledge)*.

## Explanation
For the [[investing-apprentice]], the proposed limits on a $1,000 CAD account are below. They are waiting for Stellan's approval in [[investing-apprentice-plan]].

| Rule | Limit | On $1,000 that means |
|---|---|---|
| Biggest single position | 10% | $100 |
| Most in one sector | 30% | $300 |
| Most in crypto | 20% | $200 |
| Most you can lose on one trade (to the stop) | 1% | $10 |
| Daily loss that pauses new trades | −3% | −$30 |
| Drop from peak that triggers a demotion review | −15% | −$150 |

These are *(synthesis)*: defaults proposed by Claude and accepted as "default" by Stellan on 2026-10-10 *(Stellan, 2026-10-10)*.

The limits are enforced by code, not by the AI's judgement. The AI can *propose* a trade, but the risk engine rejects any trade that breaks a limit. The AI cannot edit the limits ([[src-stellan-investing-apprentice-brief]]).

## Evidence & claims
- The agent may not rewrite its own safeguards or grant itself permissions ([[src-stellan-investing-apprentice-brief]]).
- A winning trade can still be a bad decision if it relied on unjustified risk ([[src-stellan-investing-apprentice-brief]]).

## Tensions & contradictions
- None yet.

## Related
- [[promotion-system]], [[trading-costs]], [[paper-trading]]
