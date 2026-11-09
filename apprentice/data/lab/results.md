# Strategy lab results (2026-11-09)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-21 to 2026-11-06, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3307 | -2.2% | -42.0% | -0.16 | +16.3% | -30.1% | +9.8% (SPY) | +9.9% | ❌ |
| sma_cross | 16 | 859 | +8.9% | -25.5% | 0.76 | +16.3% | -30.1% | +9.8% (SPY) | +10.9% | ❌ |
| momentum | 16 | 390 | +21.8% | -44.4% | 0.77 | +16.3% | -30.1% | +9.8% (SPY) | +37.4% | ✅ |
| momentum_buffer | 16 | 434 | +13.7% | -42.2% | 0.60 | +16.3% | -30.1% | +9.8% (SPY) | +26.5% | ❌ |
| rsi2 | 16 | 6728 | -70.8% | -100.0% | -6.34 | +16.3% | -30.1% | +9.8% (SPY) | +5.2% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
