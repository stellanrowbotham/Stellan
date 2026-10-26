# Strategy lab results (2026-10-26)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-07 to 2026-10-23, 25 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 16 | +10.2% | -19.4% | 1.01 | +18.4% | -30.1% | +11.9% (SPY) | ❌ |
| sma_cross | 16 | +11.5% | -25.4% | 0.98 | +18.4% | -30.1% | +11.9% (SPY) | ❌ |
| momentum | 16 | +31.4% | -38.0% | 1.00 | +18.4% | -30.1% | +11.9% (SPY) | ✅ |

Passing rules: momentum

## crypto (2024-11-05 to 2026-10-25, 5 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 2 | +0.1% | -13.8% | 0.13 | +10.9% | -28.3% | +19.1% (XBTCAD) | ❌ |
| sma_cross | 2 | -33.1% | -22.7% | -1.83 | +10.9% | -28.3% | +19.1% (XBTCAD) | ❌ |
| momentum | 2 | -19.4% | -14.8% | -1.64 | +10.9% | -28.3% | +19.1% (XBTCAD) | ❌ |

Passing rules: none

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- Crypto history is about 2 years, too short to trust much.
- Past results do not guarantee future results.
