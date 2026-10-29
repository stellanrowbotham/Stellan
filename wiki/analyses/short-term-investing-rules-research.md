---
type: analysis
title: Short-Term Investing Rules Research
aliases: [new apprentice rules, short-term trading research]
tags: [investing, apprentice, rules, research]
created: 2026-10-29
updated: 2026-10-29
sources: []
question: What are the best evidence-backed rules and ways to make money short-term, and which new rules could the Investing Apprentice test?
---

# Short-term investing rules: what the evidence says
> Filed from a query on 2026-10-29. Web research through the Firecrawl connector. This is not yet backed by source pages in `raw/`.

## Answer

### 1. The hard truth about short-term trading
- Most people who trade very short-term lose money. In Brazil, 97% of day traders who kept going for more than 300 days lost money. Only 1.1% earned more than the minimum wage ([Chague et al., 2020](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101)). A Taiwan study found the same pattern ([Barber, Lee, Liu & Odean](http://www.econ.yale.edu/~shiller/behfin/2004-04-10/barber-lee-liu-odean.pdf)).
- The apprentice already shows why: each US trade pays about 1.5% currency conversion each way, about 3% per round trip. Apple's one-day trade lost C$2.94, almost all of it fees. JNJ's +4.3% win lost about 40% of its gross gain to fees. *(synthesis, from the apprentice ledger 2026-10-28/29)*
- So the edge has to be bigger than the costs, or the costs have to shrink. Trading more often makes this worse. *(synthesis)*

### 2. Fundamentals: what actually drives returns (plain words)
- **A stock is a slice of a business.** Over years, the price follows the company's profits and cash flow. Over days, it is mostly noise and emotion. *(general knowledge)*
- **Quality / profitability:** companies with high gross profits relative to their assets have earned higher returns ([Novy-Marx 2013](https://www.sciencedirect.com/science/article/abs/pii/S0304405X13000044)). The effect holds internationally with similar measures such as ROE and operating profitability ([Alpha Architect](https://alphaarchitect.com/the-profitability-factor-international-evidence/)).
- **Momentum:** things that have gone up for 3–12 months tend to keep going up for a while. This is the rule the apprentice already uses, and it is the only stock rule that passes the lab. Trend-following has worked across about 140 years of data in many markets ([Hurst, Ooi & Pedersen](https://fairmodel.econ.yale.edu/ec439/hurst.pdf); [Moskowitz, Ooi & Pedersen 2012](https://www.sciencedirect.com/science/article/pii/S0304405X11002613)).
- **Costs and risk control matter more than clever picks.** That means stops, position size, diversification and low fees. *(general knowledge)*

### 3. Candidate new rules for the strategy lab
Each rule must pass the walk-forward lab after costs before it can trade. Ranked by how strong the evidence is and how well it fits the apprentice. *(synthesis)*

| # | Rule | Idea | Evidence | Fit / worry |
|---|---|---|---|---|
| 1 | **Rank buffer for momentum** | Buy when a stock enters the top 5; only sell when it falls below about rank 10 | Cuts turnover. Today's AAPL and JNJ churn shows the cost | Best fit. Directly cuts the ~3% FX churn |
| 2 | **Volatility targeting** | Size each position so each one carries the same risk | Core part of the trend-following research ([Hurst et al.](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)) | Smoother ride; small code change |
| 3 | **RSI(2) pullback, only above the 200-day average** | Buy a strong stock after a 1–2 day panic (RSI(2) < 10), sell when RSI(2) > 70–80 | Popular and well backtested ([StockCharts](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/rsi-2); [QuantifiedStrategies](https://www.quantifiedstrategies.com/rsi-2-strategy/)), but some testers say the edge is fading ([Quantitativo](https://www.quantitativo.com/p/squeezing-more-profits-with-cumulative)) | True short-term rule (days). Many trades, so it only works if fees are low. Best on CAD/TSX assets |
| 4 | **Post-earnings drift** | After a big earnings beat, hold for a few weeks | Weaker than it used to be, but 2025 papers say it is still alive ([UCLA Anderson Review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/); [Quantpedia](https://quantpedia.com/strategies/post-earnings-announcement-effect)) | Needs an earnings-surprise data feed; medium effort |
| 5 | **Quality filter on momentum** | Only buy momentum stocks with high profitability | [Novy-Marx 2013](https://www.sciencedirect.com/science/article/abs/pii/S0304405X13000044) | Needs fundamentals data (SEC EDGAR is already connected) |
| 6 | **Cut FX costs** | Prefer CAD-listed assets, or hold USD instead of converting each trade (Norbert's Gambit with DLR) | [Questrade](https://www.questrade.com/learning/investing-basics/norberts-gambit-currency-conversion), [Wealthsimple](https://help.wealthsimple.com/hc/en-ca/articles/45418222943131-Convert-currency-with-Norbert-s-Gambit) | Not a signal, but likely the biggest easy win. Small amounts may not justify the extra steps |

### 4. What does NOT work well
- **Day trading:** most people lose (see §1).
- **Many tiny trades on a C$1,000 account:** fees eat the edge. *(synthesis)*
- **Crypto rules:** only 2 test periods so far, so the evidence is weak, and the crypto momentum rule failed the lab on 2026-10-29. *(apprentice lab, 2026-10-29)*

## Basis
- Pages used: [[investing-apprentice]], [[trading-costs]], [[risk-management]], [[paper-trading]], [[look-ahead-bias]]
- Web search via Firecrawl, 2026-10-29. External sources are linked inline and have not been ingested into `raw/`.
- → Any new rule needs a code change and a lab test before it can trade. Stellan must approve the change.
