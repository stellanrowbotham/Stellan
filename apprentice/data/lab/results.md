# Strategy lab results (2026-11-17)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2007-01-03 to 2026-11-16, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3316 | -2.3% | -42.1% | -0.17 | +16.2% | -30.1% | +9.9% (SPY) | +9.9% | ❌ |
| sma_cross | 16 | 855 | +8.9% | -25.5% | 0.76 | +16.2% | -30.1% | +9.9% (SPY) | +11.0% | ❌ |
| momentum | 16 | 335 | +20.9% | -50.8% | 0.72 | +16.2% | -30.1% | +9.9% (SPY) | +43.6% | ✅ |
| momentum_buffer | 16 | 430 | +11.8% | -44.5% | 0.54 | +16.2% | -30.1% | +9.9% (SPY) | +28.0% | ❌ |
| rsi2 | 16 | 6698 | -70.8% | -100.0% | -6.35 | +16.2% | -30.1% | +9.9% (SPY) | +5.1% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
