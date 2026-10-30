# Strategy lab results (2026-10-30)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-13 to 2026-10-29, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3299 | -1.9% | -42.1% | -0.13 | +16.6% | -30.1% | +10.3% (SPY) | +10.2% | ❌ |
| sma_cross | 16 | 856 | +9.2% | -25.5% | 0.78 | +16.6% | -30.1% | +10.3% (SPY) | +11.5% | ❌ |
| momentum | 16 | 323 | +14.5% | -49.8% | 0.58 | +16.6% | -30.1% | +10.3% (SPY) | +40.2% | ❌ |
| momentum_buffer | 16 | 370 | +17.5% | -36.9% | 0.71 | +16.6% | -30.1% | +10.3% (SPY) | +31.7% | ✅ |
| rsi2 | 16 | 6745 | -71.0% | -100.0% | -6.40 | +16.6% | -30.1% | +10.3% (SPY) | +5.2% | ❌ |

Passing rules: momentum_buffer

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
