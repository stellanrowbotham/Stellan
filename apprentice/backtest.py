"""Walk-forward evaluation for proposed strategy changes (the separate evaluation environment).

A strategy is a function signal(bars_so_far, params) -> "buy" | "sell" | None that can only see bars
up to the current day (enforced by slicing). Each fold tunes nothing on its test window: params are
chosen on the training window, then frozen for the out-of-sample window. Costs are applied on every
fill. Results are compared with buy-and-hold over the same windows."""


def run(bars, signal, params, cost_pct, start, end):
    cash, qty, equity = 1.0, 0.0, []
    for i in range(start, end):
        hist = bars[: i + 1]  # no look-ahead: today's close is the latest bar
        px = bars[i]["close"]
        s = signal(hist, params)
        if s == "buy" and qty == 0:
            qty, cash = cash * (1 - cost_pct) / px, 0.0
        elif s == "sell" and qty > 0:
            cash, qty = qty * px * (1 - cost_pct), 0.0
        equity.append(cash + qty * px)
    if qty > 0:
        equity[-1] = qty * bars[end - 1]["close"] * (1 - cost_pct)
    return equity[-1] - 1 if equity else 0.0, equity


def walk_forward(bars, signal, param_grid, cost_pct, train=120, test=40):
    folds, i = [], train
    while i + test <= len(bars):
        best = max(param_grid, key=lambda p: run(bars, signal, p, cost_pct, i - train, i)[0])
        oos, _ = run(bars, signal, best, cost_pct, i, i + test)
        bh = bars[i + test - 1]["close"] / bars[i]["close"] - 1 - 2 * cost_pct
        folds.append({"train": [i - train, i], "test": [i, i + test], "params": best, "oos_return": oos, "buy_hold": bh,
                      "beat": oos > bh})
        i += test
    return {"folds": folds, "n": len(folds), "oos_mean": sum(f["oos_return"] for f in folds) / len(folds) if folds else None,
            "beat_rate": sum(f["beat"] for f in folds) / len(folds) if folds else None}


def sma_cross(hist, p):
    """Example strategy: buy when the fast SMA is above the slow SMA."""
    if len(hist) < p["slow"]:
        return None
    c = [b["close"] for b in hist]
    fast, slow = sum(c[-p["fast"]:]) / p["fast"], sum(c[-p["slow"]:]) / p["slow"]
    return "buy" if fast > slow else "sell"
