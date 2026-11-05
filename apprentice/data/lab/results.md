# Strategy lab results (2026-11-05)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-20 to 2026-11-05, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3311 | -2.1% | -42.3% | -0.15 | +16.4% | -30.1% | +9.9% (SPY) | +10.0% | ❌ |
| sma_cross | 16 | 858 | +9.0% | -25.5% | 0.77 | +16.4% | -30.1% | +9.9% (SPY) | +11.0% | ❌ |
| momentum | 16 | 295 | +20.8% | -48.0% | 0.72 | +16.4% | -30.1% | +9.9% (SPY) | +35.2% | ✅ |
| momentum_buffer | 16 | 350 | +20.7% | -39.7% | 0.80 | +16.4% | -30.1% | +9.9% (SPY) | +30.9% | ✅ |
| rsi2 | 16 | 6726 | -70.8% | -100.0% | -6.35 | +16.4% | -30.1% | +9.9% (SPY) | +4.8% | ❌ |

Passing rules: momentum, momentum_buffer

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
