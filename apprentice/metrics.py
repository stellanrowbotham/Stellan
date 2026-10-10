"""Performance statistics. Nothing is computed when there isn't enough data; the result says so."""
import math
from datetime import timedelta

from .ledger import parse_ts
from .market_calendar import ET

MIN_DAYS_FOR_RISK_ADJUSTED = 20


def daily_equity(valuations):
    """Last valuation of each Toronto calendar day -> [(date, equity)]."""
    by = {}
    for v in valuations:
        by[parse_ts(v["at"]).astimezone(ET).date()] = v["equity"]
    return sorted(by.items())


def max_drawdown(values):
    peak, mdd = -math.inf, 0.0
    for v in values:
        peak = max(peak, v)
        if peak > 0:
            mdd = min(mdd, v / peak - 1)
    return mdd


def period_return(valuations, now, days, start_equity):
    eq = daily_equity(valuations)
    if not eq:
        return None
    cutoff = (now - timedelta(days=days)).astimezone(ET).date()
    before = [e for d, e in eq if d <= cutoff]
    base = before[-1] if before else start_equity
    return eq[-1][1] / base - 1


def risk_adjusted(valuations):
    eq = [e for _, e in daily_equity(valuations)]
    if len(eq) < MIN_DAYS_FOR_RISK_ADJUSTED + 1:
        return {"available": False, "reason": f"needs {MIN_DAYS_FOR_RISK_ADJUSTED} days of history, has {max(len(eq) - 1, 0)}"}
    r = [eq[i] / eq[i - 1] - 1 for i in range(1, len(eq))]
    m = sum(r) / len(r)
    sd = math.sqrt(sum((x - m) ** 2 for x in r) / (len(r) - 1))
    dn = [min(x, 0) for x in r]
    dsd = math.sqrt(sum(x * x for x in dn) / len(dn))
    return {"available": True, "days": len(r), "sharpe": (m / sd * math.sqrt(252)) if sd > 0 else None,
            "sortino": (m / dsd * math.sqrt(252)) if dsd > 0 else None, "note": "daily returns, risk-free rate taken as 0"}


def trade_stats(closed):
    if not closed:
        return {"closed": 0}
    pnl = [t["exit"]["realized_pnl_cad"] for t in closed]
    wins, losses = [p for p in pnl if p > 0], [p for p in pnl if p <= 0]
    best = max(closed, key=lambda t: t["exit"]["realized_pnl_cad"])
    worst = min(closed, key=lambda t: t["exit"]["realized_pnl_cad"])

    def group(key):
        g = {}
        for t in closed:
            k = key(t)
            d = g.setdefault(k, {"trades": 0, "pnl_cad": 0.0, "wins": 0})
            d["trades"] += 1
            d["pnl_cad"] += t["exit"]["realized_pnl_cad"]
            d["wins"] += t["exit"]["realized_pnl_cad"] > 0
        return g

    def bucket(t):
        d = t["exit"]["holding_days"]
        return "intraday" if d < 1 else "1-5 days" if d <= 5 else "6-30 days" if d <= 30 else "30+ days"

    return {"closed": len(closed), "win_rate": len(wins) / len(pnl),
            "avg_win_cad": sum(wins) / len(wins) if wins else None, "avg_loss_cad": sum(losses) / len(losses) if losses else None,
            "profit_factor": (sum(wins) / -sum(losses)) if losses and sum(losses) < 0 else None,
            "best": {"symbol": best["symbol"], "pnl_cad": best["exit"]["realized_pnl_cad"], "trade_id": best["trade_id"]},
            "worst": {"symbol": worst["symbol"], "pnl_cad": worst["exit"]["realized_pnl_cad"], "trade_id": worst["trade_id"]},
            "by_asset": group(lambda t: t["symbol"]), "by_strategy": group(lambda t: t["strategy"]),
            "by_holding_period": group(bucket),
            "largest_profit_share": (max(wins) / sum(wins)) if wins else None}


def benchmark_return(book, symbol, start, now, usdcad_fn=None):
    """Benchmark change from the first stored quote on/after start to the latest before now."""
    first = book.first_after(symbol, start, now, tolerance_minutes=60 * 24 * 7)
    last = book.latest(symbol, now)
    if not first or not last or first["id"] == last["id"]:
        return None
    p0 = first.get("price") or (first["bid"] + first["ask"]) / 2
    p1 = last.get("price") or (last["bid"] + last["ask"]) / 2
    return p1 / p0 - 1
