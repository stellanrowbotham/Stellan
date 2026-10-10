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

The simulator copies **Questrade**, which Stellan chose on 2026-10-10 *(Stellan, 2026-10-10)*. These figures are **to be verified against the official fee schedule before Level 3**:
- Stocks and ETFs: $0 commission on online trades since early 2025 *(unverified, secondary reviews read 2026-10-10)*
- US stocks from a CAD account: about 1.5% currency conversion each way; one review says 1.99% *(unverified, secondary reviews read 2026-10-10)*
- Fractional shares: reportedly US-only. The simulator assumes **whole shares only** to stay on the safe side *(synthesis)*
- Crypto: no Questrade crypto data was found, so crypto uses Kraken's real bid/ask plus about 0.40% taker fee *(unverified, general knowledge)*
- Slippage: half the quoted spread, plus extra for thinly traded assets *(synthesis)*

## Evidence & claims
- The brief requires commissions, bid-ask spreads, slippage and crypto fees in every simulated trade ([[src-stellan-investing-apprentice-brief]]).
- Crypto costs vary by platform, and prices differ between exchanges ([[src-stellan-investing-apprentice-brief]]).

## Tensions & contradictions
- ⚠️ Secondary reviews disagree on Questrade's FX fee (1.5% vs about 2% vs 1.99%). Status: open, so the simulator uses 1.5% until the official page is checked.
- Earlier Wealthsimple figures (crypto spread 0.05–2% vs 1.5–2%) no longer apply, since Questrade was chosen.

## Related
- [[paper-trading]], [[risk-management]]
