# Strategy lab results (2026-10-19)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-11-30 to 2026-10-16, 25 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 16 | +10.3% | -19.4% | 1.02 | +18.5% | -30.1% | +12.0% (SPY) | ❌ |
| sma_cross | 16 | +11.5% | -25.4% | 0.98 | +18.5% | -30.1% | +12.0% (SPY) | ❌ |
| momentum | 16 | +36.6% | -42.4% | 1.13 | +18.5% | -30.1% | +12.0% (SPY) | ✅ |

Passing rules: momentum

## crypto (2024-10-29 to 2026-10-18, 5 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 2 | -10.0% | -13.0% | -0.24 | +12.8% | -28.3% | +24.6% (XBTCAD) | ❌ |
| sma_cross | 2 | -34.5% | -20.6% | -1.98 | +12.8% | -28.3% | +24.6% (XBTCAD) | ❌ |
| momentum | 2 | -6.7% | -11.6% | -0.30 | +12.8% | -28.3% | +24.6% (XBTCAD) | ❌ |

Passing rules: none

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- Crypto history is about 2 years, too short to trust much.
- Past results do not guarantee future results.
