---
type: concept
title: Trading costs (fees, spread, slippage)
aliases: ["Trading frictions", "Transaction costs", "Bid-ask spread", "Slippage", "FX fee"]
tags: [investing]
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Trading costs (fees, spread, slippage)
The small amounts you lose every time you buy or sell. They add up fast, especially with a small account.

## In plain words
- **Commission:** a fee the app charges per trade.
- **Spread:** shops buy from you a little cheaper than they sell to you. That gap is the spread.
- **Slippage:** by the time your order goes through, the price has moved a bit.
- **FX fee:** turning Canadian dollars into US dollars to buy a US stock costs extra.

*(general knowledge)*

## Explanation
With $1,000, costs matter a lot. A 1.5% currency fee on a $100 US-stock buy is $1.50 going in and about $1.50 coming out. The trade has to gain about 3% just to break even *(synthesis)*. That's one reason the Canadian-first focus makes sense: buying TSX stocks in CAD avoids the FX fee *(synthesis)*.

Working assumptions for the simulator, modelled on a typical Canadian app such as Wealthsimple. These are **to be verified against the official fee schedule before use**:
- Canadian stocks and ETFs: $0 commission *(unverified, secondary reviews read 2026-10-10)*
- US stocks from a CAD account: about 1.5% FX fee each way *(unverified, secondary reviews read 2026-10-10)*
- Crypto: about 1.5–2% spread on the basic tier *(unverified, secondary reviews read 2026-10-10)*
- Slippage: half the quoted spread, plus extra for thinly traded assets *(synthesis)*

## Evidence & claims
- The brief requires commissions, bid-ask spreads, slippage and crypto fees in every simulated trade ([[src-stellan-investing-apprentice-brief]]).
- Crypto costs vary by platform, and prices differ between exchanges ([[src-stellan-investing-apprentice-brief]]).

## Tensions & contradictions
- ⚠️ Secondary reviews disagree on the crypto spread (0.05–2% vs 1.5–2%). Status: open until the official schedule is checked.

## Related
- [[paper-trading]], [[risk-management]]
