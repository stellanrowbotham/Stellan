# Strategy lab results (2026-11-04)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-18 to 2026-11-03, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3305 | -2.0% | -42.2% | -0.14 | +16.5% | -30.1% | +10.1% (SPY) | +10.1% | ❌ |
| sma_cross | 16 | 860 | +9.1% | -25.5% | 0.78 | +16.5% | -30.1% | +10.1% (SPY) | +11.4% | ❌ |
| momentum | 16 | 373 | +23.1% | -51.6% | 0.82 | +16.5% | -30.1% | +10.1% (SPY) | +35.0% | ✅ |
| momentum_buffer | 16 | 428 | +13.6% | -42.3% | 0.60 | +16.5% | -30.1% | +10.1% (SPY) | +30.4% | ❌ |
| rsi2 | 16 | 6749 | -70.8% | -100.0% | -6.36 | +16.5% | -30.1% | +10.1% (SPY) | +5.6% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
