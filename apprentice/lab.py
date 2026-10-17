"""Strategy lab: walk-forward, out-of-sample tests of simple rules on real daily history, after costs.

Rules (each with a small parameter grid):
  trend      hold an asset only while its close is above its N-day moving average
  sma_cross  hold while the fast moving average is above the slow one
  momentum   every ~month, hold the top K assets by past L-day return (skipping the last 21 days),
             only if that return is positive and the asset is above its 200-day average; else cash

Walk-forward: choose the parameter that did best on the previous TRAIN window, then run it unchanged
on the next TEST window. Only TEST windows count. Signals use the close of day t and earn day t+1's
return, so no rule ever sees the future. Costs are charged on every change in holdings.

Honest limits, printed with every result: the asset list is today's survivors (survivorship bias
flatters results), end-of-day data only, and past results do not guarantee future ones."""
import json
import math
from datetime import date
from pathlib import Path

from . import history
from .ledger import iso, utcnow

OUT = Path(__file__).resolve().parent / "data" / "lab"
COST = {"us": 0.0015, "crypto": 0.005}  # per unit of turnover: spread+slippage (US, USD held) / Kraken fee+slippage
PERIODS = {"us": 252, "crypto": 365}
WINDOWS = {"us": (3, 1), "crypto": (0.75, 0.25)}  # (train years, test years); crypto history is only ~2 years
GRIDS = {
    "trend": [{"n": n} for n in (50, 100, 150, 200)],
    "sma_cross": [{"fast": 20, "slow": 100}, {"fast": 50, "slow": 200}],
    "momentum": [{"lookback": L, "top": k} for L in (63, 126, 252) for k in (2, 3, 5)],
}
LIMITS = ["Asset list is today's survivors (companies that did badly and vanished are missing), which flatters results.",
          "End-of-day prices only; real fills can be worse.",
          "Crypto history is about 2 years, too short to trust much.",
          "Past results do not guarantee future results."]


# ---------------------------------------------------------------- data
def panel(symbols):
    """Aligned close prices: dates where the benchmark (first symbol) traded; others forward-filled."""
    docs = {s: history.load(s) for s in symbols}
    docs = {s: d for s, d in docs.items() if d and len(d["bars"]) > 260}
    if not docs:
        return [], {}
    base = next(iter(docs))
    dates = [b["date"] for b in docs[base]["bars"]]
    closes = {}
    for s, d in docs.items():
        m = {b["date"]: b["close"] for b in d["bars"]}
        seq, last = [], None
        for dt in dates:
            last = m.get(dt, last)
            seq.append(last)
        closes[s] = seq
    return dates, closes


_SMA = {}


def _sma(xs, i, n):
    """n-day simple moving average at index i, computed once per series via a running sum."""
    key = (id(xs), n)
    arr = _SMA.get(key)
    if arr is None or len(arr) != len(xs):
        arr, run, valid = [None] * len(xs), 0.0, 0
        for k, v in enumerate(xs):
            if v is None:
                run, valid = 0.0, 0
                continue
            run += v
            valid += 1
            if valid > n:
                run -= xs[k - n]
                valid = n
            if valid == n:
                arr[k] = run / n
        _SMA[key] = arr
    return arr[i]


# ---------------------------------------------------------------- rules -> target weights on day i (using data up to i)
def weights(rule, p, closes, i, held=None):
    syms = list(closes)
    if rule == "trend":
        on = [s for s in syms if closes[s][i] and (m := _sma(closes[s], i, p["n"])) and closes[s][i] > m]
        return {s: 1 / len(syms) for s in on}
    if rule == "sma_cross":
        on = []
        for s in syms:
            f, sl = _sma(closes[s], i, p["fast"]), _sma(closes[s], i, p["slow"])
            if f and sl and f > sl:
                on.append(s)
        return {s: 1 / len(syms) for s in on}
    if rule == "momentum":
        if held is not None and i % 21:
            return held  # rebalance about monthly
        L, skip = p["lookback"], 21
        scores = []
        for s in syms:
            c = closes[s]
            if i - L - skip < 0 or not c[i - skip] or not c[i - L - skip]:
                continue
            mom = c[i - skip] / c[i - L - skip] - 1
            m200 = _sma(c, i, 200)
            if mom > 0 and m200 and c[i] > m200:
                scores.append((mom, s))
        top = [s for _, s in sorted(scores, reverse=True)[:p["top"]]]
        return {s: 1 / p["top"] for s in top}
    if rule == "buy_hold":
        return {s: 1 / len(syms) for s in syms}
    raise ValueError(rule)


def simulate(rule, p, closes, start, end, cost):
    """Daily returns over (start, end]; holdings set at close of i earn return of i+1."""
    rets, w, turnover, trades = [], {}, 0.0, 0
    for i in range(start, end):
        nw = weights(rule, p, closes, i, held=w if rule == "momentum" and i > start else None)
        chg = sum(abs(nw.get(s, 0) - w.get(s, 0)) for s in set(nw) | set(w))
        trades += sum(1 for s in set(nw) | set(w) if abs(nw.get(s, 0) - w.get(s, 0)) > 1e-9)
        turnover += chg
        w = nw
        r = 0.0
        for s, x in w.items():
            a, b = closes[s][i], closes[s][i + 1]
            if a and b:
                r += x * (b / a - 1)
        rets.append(r - cost * chg)
    return rets, turnover, trades


def stats(rets, periods):
    if not rets:
        return {}
    eq, peak, mdd = 1.0, 1.0, 0.0
    for r in rets:
        eq *= 1 + r
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1)
    yrs = len(rets) / periods
    m = sum(rets) / len(rets)
    sd = math.sqrt(sum((r - m) ** 2 for r in rets) / max(len(rets) - 1, 1))
    return {"total_return": eq - 1, "cagr": eq ** (1 / yrs) - 1 if yrs > 0 else None, "max_drawdown": mdd,
            "sharpe": (m / sd * math.sqrt(periods)) if sd > 0 else None, "days": len(rets)}


def walk_forward(rule, closes, kind, train_years=None, test_years=None):
    per = PERIODS[kind]
    train_years = train_years or WINDOWS[kind][0]
    test_years = test_years or WINDOWS[kind][1]
    n = len(next(iter(closes.values())))
    train, test = int(train_years * per), int(test_years * per)
    warm = 260
    folds, oos, bench, index = [], [], [], []
    first = next(iter(closes))
    i = warm + train
    while i + 2 <= n:
        j = min(i + test, n - 1)
        if j - i < int(test_years * per * 0.6):
            break
        best = max(GRIDS[rule], key=lambda p: stats(simulate(rule, p, closes, i - train, i, COST[kind])[0], per).get("sharpe") or -9)
        r, to, tr = simulate(rule, best, closes, i, j, COST[kind])
        b, _, _ = simulate("buy_hold", {}, closes, i, j, COST[kind])
        ix, _, _ = simulate("buy_hold", {}, {first: closes[first]}, i, j, COST[kind])
        index += ix
        folds.append({"test_days": [i, j], "params": best, "strategy": stats(r, per), "buy_hold": stats(b, per), "trades": tr})
        oos += r
        bench += b
        i = j
    s, bs = stats(oos, per), stats(bench, per)
    passes = bool(len(folds) >= 2 and s and bs and (
        s["cagr"] > bs["cagr"] or ((s["sharpe"] or 0) > (bs["sharpe"] or 0) + 0.1 and s["max_drawdown"] > bs["max_drawdown"])))
    latest = max(GRIDS[rule], key=lambda p: stats(simulate(rule, p, closes, max(warm, n - 1 - train), n - 1, COST[kind])[0], per).get("sharpe") or -9)
    return {"rule": rule, "folds": len(folds), "oos": s, "buy_hold_oos": bs, "index": first, "index_oos": stats(index, per),
            "passes": passes, "live_params": latest,
            "fold_detail": folds}


def run(groups=None):
    """groups: name -> (kind, [symbols]). Defaults: US stocks+ETFs, and crypto."""
    from .settings import Settings
    st = Settings()
    if groups is None:
        us = [a["symbol"] for a in st.universe if a["exchange"] == "US"]
        crypto = [a["symbol"] for a in st.universe if a["asset_type"] == "crypto"]
        groups = {"us_stocks_etfs": ("us", ["SPY"] + [s for s in us if s != "SPY"]),
                  "crypto": ("crypto", ["XBTCAD"] + [s for s in crypto if s != "XBTCAD"])}
    out = {"run_at": iso(utcnow()), "limits": LIMITS, "costs_per_turnover": COST, "groups": {}}
    for name, (kind, syms) in groups.items():
        dates, closes = panel(syms)
        if not closes:
            out["groups"][name] = {"error": "no history cached"}
            continue
        res = {r: walk_forward(r, closes, kind) for r in GRIDS}
        out["groups"][name] = {"kind": kind, "symbols": list(closes), "from": dates[0], "to": dates[-1],
                               "benchmark": "equal-weight buy-and-hold of the same assets", "rules": res,
                               "passing": [r for r, v in res.items() if v["passes"]]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(out, indent=1, default=str))
    (OUT / "results.md").write_text(markdown(out))
    return out


def latest():
    p = OUT / "results.json"
    return json.loads(p.read_text()) if p.exists() else None


def markdown(out):
    pct = lambda x: "n/a" if x is None else f"{x * 100:+.1f}%"
    lines = [f"# Strategy lab results ({out['run_at'][:10]})", "",
             "Every number below comes from test years the rule was **not** tuned on, after trading costs.", ""]
    for g, v in out["groups"].items():
        if "error" in v:
            lines += [f"## {g}: {v['error']}", ""]
            continue
        lines += [f"## {g} ({v['from']} to {v['to']}, {len(v['symbols'])} assets)", "",
                  "| Rule | Test folds | Yearly return | Worst drop | Sharpe | Buy & hold yearly | Buy & hold worst drop | Index only yearly | Passes? |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for r, x in v["rules"].items():
            s, b = x["oos"], x["buy_hold_oos"]
            lines.append(f"| {r} | {x['folds']} | {pct(s.get('cagr'))} | {pct(s.get('max_drawdown'))} | "
                         f"{(s.get('sharpe') or 0):.2f} | {pct(b.get('cagr'))} | {pct(b.get('max_drawdown'))} | "
                         f"{pct(x['index_oos'].get('cagr'))} ({x['index']}) | {'✅' if x['passes'] else '❌'} |")
        lines += ["", f"Passing rules: {', '.join(v['passing']) or 'none'}", ""]
    lines += ["## Limits", ""] + [f"- {l}" for l in out["limits"]]
    return "\n".join(lines) + "\n"
