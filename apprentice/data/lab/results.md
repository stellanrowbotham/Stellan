# Strategy lab results (2026-10-23)

Every number below comes from test years the rule was **not** tuned on, after trading costs.

## us_stocks_etfs (2006-12-06 to 2026-10-22, 25 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 16 | +10.3% | -19.4% | 1.02 | +18.5% | -30.1% | +12.0% (SPY) | ❌ |
| sma_cross | 16 | +11.1% | -25.4% | 0.95 | +18.5% | -30.1% | +12.0% (SPY) | ❌ |
| momentum | 16 | +37.4% | -35.4% | 1.16 | +18.5% | -30.1% | +12.0% (SPY) | ✅ |

Passing rules: momentum

## crypto (2024-11-02 to 2026-10-22, 5 assets)

| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |
|---|---|---|---|---|---|---|---|---|
| trend | 2 | -3.9% | -13.8% | -0.03 | +13.1% | -28.3% | +28.2% (XBTCAD) | ❌ |
| sma_cross | 2 | -36.8% | -22.7% | -2.13 | +13.1% | -28.3% | +28.2% (XBTCAD) | ❌ |
| momentum | 2 | -25.8% | -14.8% | -2.33 | +13.1% | -28.3% | +28.2% (XBTCAD) | ❌ |

Passing rules: none

## Limits

- Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.
- End-of-day prices only; real fills can be worse.
- Crypto history is about 2 years, too short to trust much.
- Past results do not guarantee future results.
