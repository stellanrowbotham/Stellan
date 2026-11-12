# Strategy lab results (2026-11-12)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-27 to 2026-11-11, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3313 | -2.1% | -42.1% | -0.15 | +16.4% | -30.1% | +10.1% (SPY) | +10.0% | ❌ |
| sma_cross | 16 | 909 | +8.9% | -25.5% | 0.76 | +16.4% | -30.1% | +10.1% (SPY) | +11.0% | ❌ |
| momentum | 16 | 329 | +24.6% | -52.4% | 0.82 | +16.4% | -30.1% | +10.1% (SPY) | +37.3% | ✅ |
| momentum_buffer | 16 | 412 | +16.5% | -43.1% | 0.69 | +16.4% | -30.1% | +10.1% (SPY) | +28.7% | ✅ |
| rsi2 | 16 | 6716 | -70.7% | -100.0% | -6.32 | +16.4% | -30.1% | +10.1% (SPY) | +5.5% | ❌ |

Passing rules: momentum, momentum_buffer

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
