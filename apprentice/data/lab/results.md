# Strategy lab results (2026-10-29)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-12 to 2026-10-28, 25 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 16 | +10.2% | -19.4% | 1.02 | +18.4% | -30.1% | +12.0% (SPY) | ❌ |
| sma_cross | 16 | +11.5% | -25.4% | 0.98 | +18.4% | -30.1% | +12.0% (SPY) | ❌ |
| momentum | 16 | +31.8% | -40.4% | 1.04 | +18.4% | -30.1% | +12.0% (SPY) | ✅ |

Passing rules: momentum

## crypto (2024-11-08 to 2026-10-28, 5 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 2 | +4.1% | -16.2% | 0.28 | +0.8% | -28.3% | +11.7% (XBTCAD) | ✅ |
| sma_cross | 2 | -39.7% | -23.9% | -2.24 | +0.8% | -28.3% | +11.7% (XBTCAD) | ❌ |
| momentum | 2 | -8.2% | -15.5% | -0.32 | +0.8% | -28.3% | +11.7% (XBTCAD) | ❌ |

Passing rules: trend

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- Crypto history is about 2 years, too short to trust much.
- Past results do not guarantee future results.
