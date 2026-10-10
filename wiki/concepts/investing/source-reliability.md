---
type: concept
title: Source reliability and the source library
aliases: ["Source registry", "Reliability tiers", "Financial source library", "Corroboration"]
tags: [investing, research]
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Source reliability and the source library
Which information to trust, how much, and how to tell a real second confirmation from the same story copied twice.

## In plain words
If a company says something in its official report, that's the best evidence. A big news agency reporting it is good. Ten websites all copying that one news story still count as **one** source, not ten *(synthesis)*.

## Explanation
The [[investing-apprentice]] ranks every source into a tier and records it in a **source registry**. The registry stores the name, category, URL, how it's accessed (API / RSS / manual), whether it works right now, when it last worked, the published time, the data time, its tier and its known limits ([[src-stellan-investing-apprentice-brief]]).

Proposed tiers *(synthesis)*:
| Tier | What | Examples from the library |
|---|---|---|
| A: primary | Official filings, exchanges, government statistics | SEC EDGAR, TMX/TSX, Nasdaq, NYSE, company investor relations, Fed, Bank of Canada, Statistics Canada, BLS, BEA, US Treasury, EIA, FRED, CFTC, FINRA |
| B: licensed data | Price and fundamentals APIs | Alpha Vantage, Massive, Finnhub, Financial Modeling Prep, Twelve Data, Tiingo, Nasdaq Data Link, CoinGecko, CoinMarketCap, CoinDesk Data, DefiLlama, Kraken and Coinbase market data |
| C: reputable news | Original reporting | Reuters, AP, Bloomberg, FT, WSJ, CNBC, Barron's, MarketWatch, CoinDesk, The Block |
| D: aggregators and commentary | Useful leads that need checking | Yahoo Finance, Investing.com, StockAnalysis, TradingView, Cointelegraph, Decrypt, exchange blogs |

The library has 45 entries ([[src-stellan-investing-apprentice-brief]]). Many outlets (Bloomberg, FT, WSJ, Barron's, MarketWatch) are paywalled and their terms forbid scraping, so they are recorded as "headline/link only" unless licensed access exists *(general knowledge, to verify per site)*. For Canadian company filings, SEDAR+ isn't on the list yet but is the official source *(general knowledge)*.

## Evidence & claims
- Prefer official filings over headlines that repeat another publication. Deduplicate syndicated stories and keep the original publication time ([[src-stellan-investing-apprentice-brief]]).
- If a source is down, stale, paywalled or needs a key, record that and continue with alternatives. Never claim an integration works when it doesn't ([[src-stellan-investing-apprentice-brief]]).
- No trade is made if the price isn't fresh enough or the research is missing ([[src-stellan-investing-apprentice-brief]]).

## Tensions & contradictions
- ⚠️ Free data plans may not include TSX prices. Twelve Data's free plan has 800 calls a day and 8 a minute, and Alpha Vantage's has 25 a day. Neither result confirmed TSX coverage, which conflicts with the Canadian-first goal. Status: open, to verify in Phase 1 *(unverified, web search 2026-10-10)*.

## Related
- [[look-ahead-bias]], [[paper-trading]]
