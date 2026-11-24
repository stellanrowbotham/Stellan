# Strategy lab results (2026-11-24)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2007-01-10 to 2026-11-23, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3307 | -2.3% | -41.6% | -0.17 | +16.1% | -30.1% | +9.7% (SPY) | +9.8% | ❌ |
| sma_cross | 16 | 858 | +8.7% | -25.5% | 0.74 | +16.1% | -30.1% | +9.7% (SPY) | +11.0% | ❌ |
| momentum | 16 | 314 | +13.9% | -47.7% | 0.56 | +16.1% | -30.1% | +9.7% (SPY) | +31.6% | ❌ |
| momentum_buffer | 16 | 425 | +11.4% | -48.1% | 0.52 | +16.1% | -30.1% | +9.7% (SPY) | +28.0% | ❌ |
| rsi2 | 16 | 6715 | -70.8% | -100.0% | -6.37 | +16.1% | -30.1% | +9.7% (SPY) | +5.2% | ❌ |

Passing rules: none

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
