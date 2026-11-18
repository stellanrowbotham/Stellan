# Strategy lab results (2026-11-18)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2007-01-04 to 2026-11-17, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3301 | -2.3% | -41.6% | -0.17 | +16.1% | -30.1% | +9.7% (SPY) | +9.5% | ❌ |
| sma_cross | 16 | 857 | +8.8% | -25.5% | 0.75 | +16.1% | -30.1% | +9.7% (SPY) | +11.0% | ❌ |
| momentum | 16 | 323 | +16.2% | -47.7% | 0.62 | +16.1% | -30.1% | +9.7% (SPY) | +27.9% | ✅ |
| momentum_buffer | 16 | 408 | +15.4% | -41.8% | 0.64 | +16.1% | -30.1% | +9.7% (SPY) | +30.0% | ❌ |
| rsi2 | 16 | 6701 | -71.0% | -100.0% | -6.37 | +16.1% | -30.1% | +9.7% (SPY) | +4.3% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
