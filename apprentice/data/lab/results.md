# Strategy lab results (2026-11-27)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2007-01-12 to 2026-11-25, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3306 | -2.4% | -41.7% | -0.18 | +16.0% | -30.1% | +9.6% (SPY) | +9.7% | ❌ |
| sma_cross | 16 | 856 | +8.7% | -25.5% | 0.74 | +16.0% | -30.1% | +9.6% (SPY) | +11.1% | ❌ |
| momentum | 16 | 373 | +19.9% | -48.7% | 0.72 | +16.0% | -30.1% | +9.6% (SPY) | +35.1% | ✅ |
| momentum_buffer | 16 | 400 | +13.3% | -41.7% | 0.59 | +16.0% | -30.1% | +9.6% (SPY) | +28.6% | ❌ |
| rsi2 | 16 | 6723 | -70.9% | -100.0% | -6.37 | +16.0% | -30.1% | +9.6% (SPY) | +5.0% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
