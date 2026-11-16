# Strategy lab results (2026-11-16)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-29 to 2026-11-13, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3309 | -2.2% | -41.9% | -0.16 | +16.3% | -30.1% | +10.0% (SPY) | +9.9% | ❌ |
| sma_cross | 16 | 909 | +8.8% | -25.5% | 0.76 | +16.3% | -30.1% | +10.0% (SPY) | +11.0% | ❌ |
| momentum | 16 | 316 | +19.7% | -48.5% | 0.70 | +16.3% | -30.1% | +10.0% (SPY) | +35.9% | ✅ |
| momentum_buffer | 16 | 436 | +11.4% | -46.8% | 0.53 | +16.3% | -30.1% | +10.0% (SPY) | +23.6% | ❌ |
| rsi2 | 16 | 6714 | -70.7% | -100.0% | -6.32 | +16.3% | -30.1% | +10.0% (SPY) | +5.9% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
