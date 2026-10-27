# Strategy lab results (2026-10-27)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-08 to 2026-10-26, 25 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 16 | +10.2% | -19.4% | 1.02 | +18.4% | -30.1% | +11.9% (SPY) | ❌ |
| sma_cross | 16 | +11.5% | -25.4% | 0.97 | +18.4% | -30.1% | +11.9% (SPY) | ❌ |
| momentum | 16 | +39.4% | -37.9% | 1.21 | +18.4% | -30.1% | +11.9% (SPY) | ✅ |

Passing rules: momentum

## crypto (2024-11-06 to 2026-10-26, 5 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 2 | -6.0% | -14.2% | -0.10 | +3.1% | -28.3% | +11.7% (XBTCAD) | ❌ |
| sma_cross | 2 | -38.4% | -23.0% | -2.14 | +3.1% | -28.3% | +11.7% (XBTCAD) | ❌ |
| momentum | 2 | +0.6% | -15.2% | 0.14 | +3.1% | -28.3% | +11.7% (XBTCAD) | ❌ |

Passing rules: none

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- Crypto history is about 2 years, too short to trust much.
- Past results do not guarantee future results.
