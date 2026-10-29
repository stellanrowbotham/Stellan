"""Exports the dashboard's data as JSON documents (one per tab) plus CSV downloads. The Routine
uploads the JSON to the dashboard artifact's database. Everything comes from the ledgers, so the
dashboard can only show what is actually recorded."""
import csv
import json
from pathlib import Path

from . import forecasts as fc
from . import metrics, scorecard
from .health import source_status
from .ledger import Ledger, iso, parse_ts
from .levels import NAMES
from .market_calendar import ET
from .quotebook import QuoteBook

OUT = Path(__file__).resolve().parent / "state" / "dashboard"
EXPORTS = Path(__file__).resolve().parent / "reports" / "exports"
LIMIT = 200


def _r(x, n=4):
    return None if x is None else round(x, n)


def export(settings, broker, now, health_issues=()):
    kw = {"directory": broker.dir} if broker.dir else {}
    L = lambda n: Ledger(n, **kw).read()
    book = QuoteBook(broker.dir)
    port = broker.portfolio()
    marks = broker._marks(book, now, port)
    equity, unmarked = port.equity(marks)
    start = settings["account"]["starting_balance"]
    vals = L("valuations")
    trades = broker.trades()
    closed = [t for t in trades.values() if t["status"] == "closed"]
    open_t = [t for t in trades.values() if t["status"] == "open"]
    unreal = port.unrealized(marks)
    from .risk import halt_state
    _, _, hs = halt_state(vals, equity, now, settings)
    today_et = now.astimezone(ET).date()
    fills_today = [f for f in L("fills") if parse_ts(f["filled_at"]).astimezone(ET).date() == today_et]
    closed_today = [t for t in closed if parse_ts(t["exit"]["exit_at"]).astimezone(ET).date() == today_et]
    evals = L("evaluations")
    last_eval = evals[-1] if evals else None
    sc_rows = L("scorecard")
    fstats = fc.stats(L("forecasts"), L("forecast_scores"))
    reports = L("reports")
    heads = sorted([r for r in L("research") if r.get("kind") == "headline"], key=lambda r: r.get("published_at") or "", reverse=True)

    curve = [{"t": v["at"], "equity": _r(v["equity"], 2)} for v in vals][-500:]
    bsym = settings["benchmarks"]["CA_STOCK"]["symbol"]
    b0 = book.first_after(bsym, parse_ts(settings["account"]["start_date"] + "T00:00:00-04:00"), now, 60 * 24 * 7)
    if b0:
        p0 = b0.get("price") or (b0["bid"] + b0["ask"]) / 2
        for pt in curve:
            q = book.latest(bsym, parse_ts(pt["t"]))
            if q and parse_ts(q["observed_at"]) >= parse_ts(b0["observed_at"]):
                pt["benchmark"] = _r(start * ((q.get("price") or (q["bid"] + q["ask"]) / 2) / p0), 2)

    level = broker.level()
    docs = {
        "overview": {
            "updatedAt": iso(now), "level": level, "levelName": NAMES[level],
            "levelsEnabled": settings["agent"].get("levels_enabled", True),
            "startingBalance": start, "cash": _r(port.cash, 2), "equity": _r(equity, 2),
            "totalReturnPct": _r(equity / start - 1), "realized": _r(port.realized_total, 2),
            "unrealized": _r(sum(v for v in unreal.values() if v is not None), 2),
            "dayReturnPct": _r(metrics.period_return(vals, now, 1, start)),
            "weekReturnPct": _r(metrics.period_return(vals, now, 7, start)),
            "monthReturnPct": _r(metrics.period_return(vals, now, 30, start)),
            "maxDrawdownPct": _r(metrics.max_drawdown([start] + [v["equity"] for v in vals])),
            "riskAdjusted": metrics.risk_adjusted(vals), "equityCurve": curve, "benchmarkLabel": settings["benchmarks"]["CA_STOCK"]["label"],
            "unmarked": unmarked,
            "totalPnl": _r(equity - start, 2), "dayPnl": _r(equity - hs["start_of_day"], 2),
            "startOfDayEquity": _r(hs["start_of_day"], 2),
            "todayActivity": [{"at": f["filled_at"], "symbol": f["symbol"], "side": f["side"], "qty": f["qty"],
                               "price": _r(f["price"]), "cashCad": _r(f["cash_delta_cad"], 2), "feesCad": _r(f["fees_cad"], 2),
                               "reason": f.get("reason"),
                               "pnl": next((_r(t["exit"]["realized_pnl_cad"], 2) for t in closed_today
                                            if t["trade_id"] == f["trade_id"] and f["side"] == "sell"), None)} for f in fills_today],
            "positions": [{"tradeId": t["trade_id"], "symbol": t["symbol"], "strategy": t["strategy"], "experiment": t.get("experiment"),
                           "qty": port.positions[t["trade_id"]].qty if t["trade_id"] in port.positions else None,
                           "entry": _r(t["entry"]["entry_price"]), "stop": t["stop_price"], "target": t["target_price"],
                           "trailing": bool(t.get("trail_distance")), "rule": t.get("rule"),
                           "price": _r((book.latest(t["symbol"], now) or {}).get("price")),
                           "costBasis": _r(port.positions[t["trade_id"]].cost_basis_cad, 2) if t["trade_id"] in port.positions else None,
                           "unrealized": _r(unreal.get(t["trade_id"]), 2), "openedAt": t["entry"]["opened_at"],
                           "markCad": _r(marks.get(t["symbol"])),
                           "valueCad": _r(marks[t["symbol"]] * port.positions[t["trade_id"]].qty, 2) if t["symbol"] in marks and t["trade_id"] in port.positions else None,
                           "unrealizedPct": _r(unreal[t["trade_id"]] / port.positions[t["trade_id"]].cost_basis_cad) if unreal.get(t["trade_id"]) is not None and t["trade_id"] in port.positions else None}
                          for t in open_t],
            "headlines": [{"title": h["title"], "url": h["url"], "source": h["source_id"], "publishedAt": h.get("published_at"),
                           "syndicated": bool(h.get("syndicated_from"))} for h in heads[:15]],
            "promotion": last_eval, "health": list(health_issues),
        },
        "research": {"updatedAt": iso(now), "reports": [{k: r.get(k) for k in ("id", "run", "at", "level", "no_trade", "headline",
                                                                              "market_summary", "sources_searched", "limitations", "candidates", "md_path")}
                                                         for r in reports[-10:]][::-1]},
        "trading": {
            "updatedAt": iso(now),
            "orders": [o for o in L("orders")][-LIMIT:][::-1],
            "open": [t for t in open_t],
            "closed": [{"tradeId": t["trade_id"], "symbol": t["symbol"], "strategy": t["strategy"], "experiment": t.get("experiment"),
                        "decidedAt": t["decided_at"], "thesis": t["thesis"], "entry": _r(t["entry"]["entry_price"]),
                        "exit": _r(t["exit"]["exit_price"]), "exitReason": t["exit"]["exit_reason"], "pnl": _r(t["exit"]["realized_pnl_cad"], 2),
                        "returnPct": _r(t["exit"]["return_pct"]), "holdingDays": _r(t["exit"]["holding_days"], 2),
                        "fees": _r(t["exit"]["fees_cad"], 2)} for t in closed][-LIMIT:][::-1],
            "stats": metrics.trade_stats(closed),
            "costs": {"fees": _r(port.fees_cad, 2), "slippage": _r(port.slippage_cad, 2), "spread": _r(port.spread_cost_cad, 2)},
            "exposure": dict(zip(("bySector", "crypto"), port.exposure(marks, settings))),
        },
        "learning": {
            "updatedAt": iso(now), "forecastStats": fstats,
            "forecasts": [{**{k: f.get(k) for k in ("id", "symbol", "direction", "probability", "made_at", "horizon_end", "rationale", "strategy")},
                           "score": next((s for s in L("forecast_scores") if s["forecast_id"] == f["id"]), None)}
                          for f in L("forecasts")][-LIMIT:][::-1],
            "reviews": L("reviews")[-LIMIT:][::-1],
            "mistakes": [m | {"tradeId": r["trade_id"], "at": r["recorded_at"]} for r in L("reviews") for m in r.get("mistakes", [])][-LIMIT:][::-1],
            "lessons": [{"lesson": x, "tradeId": r["trade_id"], "symbol": r["symbol"]} for r in L("reviews") for x in r.get("lessons", [])][-LIMIT:][::-1],
            "experiments": L("experiments")[-50:][::-1],
            "lab": _lab_summary(),
        },
        "progression": {
            "updatedAt": iso(now), "level": level, "levelName": NAMES[level], "levels": NAMES,
            "levelsEnabled": settings["agent"].get("levels_enabled", True),
            "latest": last_eval, "history": [{k: e.get(k) for k in ("at", "level", "eligible", "note")} for e in evals[-60:]][::-1],
            "scorecard": scorecard.totals(sc_rows), "events": sc_rows[-LIMIT:][::-1], "levelEvents": L("level_events")[::-1],
        },
        "settings": {
            "updatedAt": iso(now), "approved": settings.approved, "account": settings["account"], "risk": settings["risk"],
            "strategies": settings["strategies"], "costs": settings["costs"], "benchmarks": settings["benchmarks"],
            "schedule": settings["schedule"], "notifications": settings["notifications"], "promotionRules": settings["promotion"],
            "permissions": {"liveTrading": False, "canPlaceSimulatedTrades": (not settings["agent"].get("levels_enabled", True)) or level >= 2, "canEditOwnRules": False,
                            "canSendEmailTo": "Stellan only"},
            "universe": settings.universe, "sources": source_status(settings, broker.dir),
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for name, doc in docs.items():
        (OUT / f"{name}.json").write_text(json.dumps(doc, default=str))
    _csv(closed, vals)
    return {name: str(OUT / f"{name}.json") for name in docs}


def _lab_summary():
    from . import lab
    res = lab.latest()
    if not res:
        return None
    out = {"runAt": res["run_at"], "limits": res["limits"], "groups": []}
    for name, g in res["groups"].items():
        if "error" in g:
            continue
        out["groups"].append({"name": name, "from": g["from"], "to": g["to"], "assets": len(g["symbols"]),
                              "rules": [{"rule": r, "folds": v["folds"], "passes": v["passes"], "params": v["live_params"],
                                         "cagr": _r(v["oos"].get("cagr")), "maxDD": _r(v["oos"].get("max_drawdown")),
                                         "sharpe": _r(v["oos"].get("sharpe"), 2), "bhCagr": _r(v["buy_hold_oos"].get("cagr")),
                                         "bhMaxDD": _r(v["buy_hold_oos"].get("max_drawdown")),
                                         "index": v.get("index"), "indexCagr": _r((v.get("index_oos") or {}).get("cagr")),
                                         "trades": v.get("trades"),
                                         "usdHeldCagr": _r(((v.get("if_usd_held") or {}).get("oos") or {}).get("cagr"))} for r, v in g["rules"].items()]})
    return out


def _csv(closed, vals):
    EXPORTS.mkdir(parents=True, exist_ok=True)
    with (EXPORTS / "trades.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["trade_id", "symbol", "strategy", "experiment", "decided_at", "entry_price", "exit_price", "exit_reason",
                    "realized_pnl_cad", "return_pct", "holding_days", "fees_cad", "thesis"])
        for t in closed:
            w.writerow([t["trade_id"], t["symbol"], t["strategy"], t.get("experiment"), t["decided_at"], t["entry"]["entry_price"],
                        t["exit"]["exit_price"], t["exit"]["exit_reason"], t["exit"]["realized_pnl_cad"], t["exit"]["return_pct"],
                        t["exit"]["holding_days"], t["exit"]["fees_cad"], t["thesis"]])
    with (EXPORTS / "equity.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["at", "equity_cad", "cash_cad", "realized_total_cad", "fees_cad", "reconciled"])
        for v in vals:
            w.writerow([v["at"], v["equity"], v["cash"], v["realized_total"], v["fees_cad"], v["reconciled"]])
