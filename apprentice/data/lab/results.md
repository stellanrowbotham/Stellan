# Strategy lab results (2026-11-20)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2007-01-08 to 2026-11-19, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3313 | -2.4% | -41.8% | -0.18 | +16.0% | -30.1% | +9.6% (SPY) | +9.8% | ❌ |
| sma_cross | 16 | 860 | +8.6% | -25.5% | 0.74 | +16.0% | -30.1% | +9.6% (SPY) | +11.0% | ❌ |
| momentum | 16 | 300 | +21.9% | -42.2% | 0.75 | +16.0% | -30.1% | +9.6% (SPY) | +36.5% | ✅ |
| momentum_buffer | 16 | 380 | +15.1% | -39.5% | 0.64 | +16.0% | -30.1% | +9.6% (SPY) | +30.5% | ❌ |
| rsi2 | 16 | 6714 | -70.9% | -100.0% | -6.36 | +16.0% | -30.1% | +9.6% (SPY) | +5.0% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
