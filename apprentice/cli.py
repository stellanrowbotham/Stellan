"""Command line for the Routines and for humans.

    python3 -m apprentice status                  one-screen summary
    python3 -m apprentice collect [--scope crypto,stocks,macro,news]
    python3 -m apprentice research-add FILE.json  add research notes (list)
    python3 -m apprentice forecast-add FILE.json  add forecasts (list)
    python3 -m apprentice forecast-score          score forecasts whose horizon has passed
    python3 -m apprentice propose FILE.json       send trade proposals (list) through the risk engine
    python3 -m apprentice exit TRADE_ID REASON    ask to close an open trade (e.g. thesis_invalidated)
    python3 -m apprentice process                 fill/expire orders, trigger stops/targets, value portfolio
    python3 -m apprentice reviews-due             closed trades that still need a review
    python3 -m apprentice review-add FILE.json    add post-trade reviews (list)
    python3 -m apprentice watch add|remove SYMBOL REASON
    python3 -m apprentice experiment-add FILE.json  propose a strategy change (needs Stellan's approval)
    python3 -m apprentice evaluate                promotion/demotion evaluation
    python3 -m apprentice report FILE.json RUN    build the research report (RUN = pre_market|post_close|crypto|day_experiment)
    python3 -m apprentice dashboard               export dashboard JSON + CSV
    python3 -m apprentice health                  health checks
    python3 -m apprentice verify                  verify every ledger hash chain + accounting
    python3 -m apprentice sources                 source registry with live status
    python3 -m apprentice approve-config          HUMAN ONLY: re-approve config after Stellan agrees to a change
    python3 -m apprentice run-start JOB           record that a scheduled job started
"""
import argparse
import json
import os
import sys
from pathlib import Path

from . import collect, dashboard, forecasts, health, promotion, report, research, reviews
from .broker import PaperBroker
from .ledger import Ledger, iso, new_id, utcnow, verify_all
from .levels import NAMES
from .settings import APPROVED_FILE, Settings, config_hash


def _load(path):
    data = json.loads(Path(path).read_text())
    return data if isinstance(data, list) else [data]


def _print(x):
    print(json.dumps(x, indent=1, default=str))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="apprentice", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("status", "forecast-score", "process", "reviews-due", "evaluate", "dashboard", "health", "verify", "sources", "approve-config"):
        sub.add_parser(name)
    c = sub.add_parser("collect")
    c.add_argument("--scope", default="crypto,stocks,macro,news")
    for name in ("research-add", "forecast-add", "propose", "review-add", "experiment-add"):
        sub.add_parser(name).add_argument("file")
    e = sub.add_parser("exit")
    e.add_argument("trade_id")
    e.add_argument("reason")
    w = sub.add_parser("watch")
    w.add_argument("action", choices=["add", "remove"])
    w.add_argument("symbol")
    w.add_argument("reason")
    r = sub.add_parser("report")
    r.add_argument("file")
    r.add_argument("run")
    rs = sub.add_parser("run-start")
    rs.add_argument("job")
    a = ap.parse_args(argv)

    now = utcnow()
    s = Settings()
    b = PaperBroker(s)

    if a.cmd == "status":
        port = b.portfolio()
        ok, *_ = port.reconcile()
        lvl = b.level()
        _print({"level": f"{lvl} ({NAMES[lvl]})", "config_approved": s.approved, "cash_cad": round(port.cash, 2),
                "open_positions": {t: p.symbol for t, p in port.positions.items()}, "realized_cad": round(port.realized_total, 2),
                "reconciled": ok, "ledger_problems": verify_all()})
    elif a.cmd == "collect":
        _print(collect.run(s, b, now, tuple(a.scope.split(","))))
    elif a.cmd == "research-add":
        added, rejected = research.add_notes(s, _load(a.file), now)
        _print({"added": [x["id"] for x in added], "rejected": rejected})
    elif a.cmd == "forecast-add":
        out = []
        for f in _load(a.file):
            rec, probs = forecasts.add(s, f, now)
            out.append({"id": rec["id"]} if rec else {"rejected": f.get("symbol"), "problems": probs})
        _print(out)
    elif a.cmd == "forecast-score":
        _print(forecasts.score_due(s, now))
    elif a.cmd == "propose":
        _print([b.propose(p, now) for p in _load(a.file)])
    elif a.cmd == "exit":
        _print(b.request_exit(a.trade_id, a.reason, now) or {"error": "trade not open, or an exit is already pending"})
    elif a.cmd == "process":
        _print(b.process(now))
    elif a.cmd == "reviews-due":
        _print([{"trade_id": t["trade_id"], "symbol": t["symbol"], "thesis": t["thesis"], "exit": t["exit"]} for t in reviews.due(b)])
    elif a.cmd == "review-add":
        _print([{"id": (rec or {}).get("id"), "problems": p} for rec, p in (reviews.add(s, b, r, now) for r in _load(a.file))])
    elif a.cmd == "watch":
        if not s.asset(a.symbol):
            print(f"{a.symbol} is not in the approved universe; propose it to Stellan in the report instead.")
            return 1
        _print(Ledger("watchlist").append({"action": a.action, "symbol": a.symbol, "reason": a.reason}, now=now))
    elif a.cmd == "experiment-add":
        out = []
        for x in _load(a.file):
            need = [k for k in ("title", "hypothesis", "change", "test_plan") if not x.get(k)]
            if need:
                out.append({"rejected": x.get("title"), "missing": need})
                continue
            out.append(Ledger("experiments").append({"id": new_id("x"), "status": "awaiting_approval", **x}, now=now))
        _print(out)
    elif a.cmd == "evaluate":
        _print(promotion.evaluate(s, b, now))
    elif a.cmd == "report":
        rec, md, html_path = report.build(s, b, _load(a.file)[0], now, a.run)
        _print({"report_id": rec["id"], "no_trade": rec["no_trade"], "headline": rec["headline"], "markdown": str(md), "html": str(html_path)})
    elif a.cmd == "dashboard":
        _print(dashboard.export(s, b, now, health.run(s, b, now)))
    elif a.cmd == "health":
        issues = health.run(s, b, now)
        _print(issues or "all checks passed")
        return 1 if any(i["level"] == "error" for i in issues) else 0
    elif a.cmd == "verify":
        probs = verify_all()
        ok, lhs, rhs = b.portfolio().reconcile()
        _print({"ledger_problems": probs, "reconciled": ok, "cash_plus_basis": lhs, "start_plus_realized": rhs})
        return 1 if probs or not ok else 0
    elif a.cmd == "sources":
        _print([{k: x[k] for k in ("n", "id", "name", "tier", "integration", "status", "last_success", "last_error")}
                for x in health.source_status(s)])
    elif a.cmd == "approve-config":
        if os.environ.get("APPRENTICE_ROUTINE"):
            print("Refused: config approval can't run inside a scheduled Routine.")
            return 2
        h = config_hash()
        APPROVED_FILE.write_text(f"{h}  settings.json+universe.json approved {iso(now)}\n")
        print(f"approved {h}")
    elif a.cmd == "run-start":
        health.record_run(a.job, now)
        print("recorded")
    return 0
