# Strategy lab results (2026-11-02)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-14 to 2026-10-30, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3297 | -2.0% | -42.0% | -0.14 | +16.5% | -30.1% | +10.1% (SPY) | +9.9% | ❌ |
| sma_cross | 16 | 857 | +9.1% | -25.5% | 0.78 | +16.5% | -30.1% | +10.1% (SPY) | +11.0% | ❌ |
| momentum | 16 | 355 | +20.1% | -48.4% | 0.71 | +16.5% | -30.1% | +10.1% (SPY) | +34.2% | ✅ |
| momentum_buffer | 16 | 398 | +17.4% | -42.0% | 0.70 | +16.5% | -30.1% | +10.1% (SPY) | +26.2% | ✅ |
| rsi2 | 16 | 6734 | -71.0% | -100.0% | -6.40 | +16.5% | -30.1% | +10.1% (SPY) | +4.8% | ❌ |

Passing rules: momentum, momentum_buffer

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
