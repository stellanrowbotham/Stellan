# Strategy lab results (2026-11-13)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-28 to 2026-11-12, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3311 | -2.1% | -41.9% | -0.15 | +16.4% | -30.1% | +10.1% (SPY) | +10.0% | ❌ |
| sma_cross | 16 | 910 | +8.9% | -25.5% | 0.76 | +16.4% | -30.1% | +10.1% (SPY) | +11.0% | ❌ |
| momentum | 16 | 337 | +21.8% | -45.6% | 0.75 | +16.4% | -30.1% | +10.1% (SPY) | +44.0% | ✅ |
| momentum_buffer | 16 | 358 | +20.6% | -39.1% | 0.79 | +16.4% | -30.1% | +10.1% (SPY) | +31.6% | ✅ |
| rsi2 | 16 | 6721 | -70.7% | -100.0% | -6.30 | +16.4% | -30.1% | +10.1% (SPY) | +6.0% | ❌ |

Passing rules: momentum, momentum_buffer

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
