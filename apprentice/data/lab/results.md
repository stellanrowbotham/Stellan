# Strategy lab results (2026-11-25)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2007-01-11 to 2026-11-24, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3298 | -2.3% | -41.3% | -0.17 | +16.0% | -30.1% | +9.6% (SPY) | +9.7% | ❌ |
| sma_cross | 16 | 853 | +8.7% | -25.5% | 0.74 | +16.0% | -30.1% | +9.6% (SPY) | +11.0% | ❌ |
| momentum | 16 | 315 | +21.7% | -55.0% | 0.74 | +16.0% | -30.1% | +9.6% (SPY) | +34.4% | ✅ |
| momentum_buffer | 16 | 414 | +13.3% | -43.3% | 0.58 | +16.0% | -30.1% | +9.6% (SPY) | +27.9% | ❌ |
| rsi2 | 16 | 6721 | -71.0% | -100.0% | -6.37 | +16.0% | -30.1% | +9.6% (SPY) | +4.7% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
