---
type: concept
title: Paper trading
aliases: ["Simulated trading", "Virtual trading", "Paper portfolio"]
tags: [investing]
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Paper trading
Practising buying and selling with pretend money, using real market prices, so you can learn without risking anything.

## In plain words
It's like playing a video game version of the stock market that uses the *real* prices. If you "buy" a share at $20 and it goes to $22, you made a pretend $2. The point is to find out whether your ideas work *before* real money is involved *(general knowledge)*.

## Explanation
Paper trading only teaches something if the simulation is honest. Three things make it honest:
1. **Real prices at the real time.** A pretend order fills only at a price that actually existed when the decision was made, with no peeking at later prices. See [[look-ahead-bias]] ([[src-stellan-investing-apprentice-brief]]).
2. **Real costs.** Commissions, the bid-ask spread, slippage and crypto fees are subtracted. See [[trading-costs]] ([[src-stellan-investing-apprentice-brief]]).
3. **A permanent record.** Each trade stores its ID, timestamps, the data available at the time, the thesis, the exit rules, and later its outcome and lessons. The original reasoning is never rewritten after the result is known ([[src-stellan-investing-apprentice-brief]]).

Paper results usually look better than real ones. Pretend orders don't move the price and don't feel scary, so even an honest simulator should be read as a best case *(general knowledge)*.

## Evidence & claims
- The [[investing-apprentice]] must start in simulation with no ability to place real orders, and simulated success never unlocks live trading by itself ([[src-stellan-investing-apprentice-brief]]).
- Market hours, holidays, price gaps, missing data and after-hours trading must be handled explicitly ([[src-stellan-investing-apprentice-brief]]).

## Tensions & contradictions
- None yet.

## Related
- [[risk-management]], [[promotion-system]]
