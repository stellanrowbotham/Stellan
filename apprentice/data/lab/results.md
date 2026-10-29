# Strategy lab results (2026-10-29)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-12 to 2026-10-28, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3304 | -1.9% | -42.2% | -0.14 | +16.6% | -30.1% | +10.3% (SPY) | +10.2% | ❌ |
| sma_cross | 16 | 852 | +9.3% | -25.5% | 0.79 | +16.6% | -30.1% | +10.3% (SPY) | +11.5% | ❌ |
| momentum | 16 | 329 | +17.9% | -47.1% | 0.67 | +16.6% | -30.1% | +10.3% (SPY) | +31.8% | ✅ |
| momentum_buffer | 16 | 404 | +17.3% | -40.0% | 0.71 | +16.6% | -30.1% | +10.3% (SPY) | +31.4% | ✅ |
| rsi2 | 16 | 6729 | -70.9% | -100.0% | -6.37 | +16.6% | -30.1% | +10.3% (SPY) | +5.3% | ❌ |

Passing rules: momentum, momentum_buffer

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
