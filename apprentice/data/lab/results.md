# Strategy lab results (2026-11-23)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2007-01-09 to 2026-11-20, 25 assets)

| Rule | Test folds | Trades | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | If USD held: yearly | Passes? |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 16 | 3307 | -2.4% | -41.6% | -0.18 | +15.8% | -30.1% | +9.4% (SPY) | +9.4% | ❌ |
| sma_cross | 16 | 856 | +8.5% | -25.5% | 0.73 | +15.8% | -30.1% | +9.4% (SPY) | +11.0% | ❌ |
| momentum | 16 | 330 | +24.0% | -42.4% | 0.79 | +15.8% | -30.1% | +9.4% (SPY) | +29.1% | ✅ |
| momentum_buffer | 16 | 439 | +13.2% | -43.1% | 0.59 | +15.8% | -30.1% | +9.4% (SPY) | +28.6% | ❌ |
| rsi2 | 16 | 6710 | -70.8% | -100.0% | -6.34 | +15.8% | -30.1% | +9.4% (SPY) | +5.1% | ❌ |

Passing rules: momentum

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- US results include the 1.5% currency conversion on every buy and sell (about 3.3% per round trip with spreads).
- Canadian (TSX) stocks have no cached daily history yet, so the lab tests US stocks and ETFs (EWC stands in for Canada).
- Past results do not guarantee future results.
