# Strategy lab results (2026-11-10)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-22 to 2026-11-09, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3312 | -2.1% | -42.2% | -0.16 | +16.4% | -30.1% | +10.0% (SPY) | +10.0% | ❌ |
| sma_cross | 16 | 909 | +8.9% | -25.5% | 0.76 | +16.4% | -30.1% | +10.0% (SPY) | +11.0% | ❌ |
| momentum | 16 | 391 | +16.0% | -55.9% | 0.63 | +16.4% | -30.1% | +10.0% (SPY) | +34.1% | ❌ |
| momentum_buffer | 16 | 402 | +18.3% | -47.8% | 0.73 | +16.4% | -30.1% | +10.0% (SPY) | +28.7% | ✅ |
| rsi2 | 16 | 6728 | -70.8% | -100.0% | -6.32 | +16.4% | -30.1% | +10.0% (SPY) | +5.1% | ❌ |

Passing rules: momentum_buffer

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
