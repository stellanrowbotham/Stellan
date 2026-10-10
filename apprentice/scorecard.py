"""Virtual scorecard. Points come only from the fixed tables in settings.json. There are no
points for volume (more trades, more research, higher confidence)."""
from .ledger import Ledger, new_id

INTEGRITY = {"fabricated_or_unsourced_fact", "timestamp_error"}
RISK = {"risk_rule_breach_attempt"}


def award(settings, kind, reason, ref=None, ledger_dir=None, now=None):
    table = {**settings["scorecard"]["rewards"], **settings["scorecard"]["penalties"]}
    if kind not in table:
        raise KeyError(f"unknown scorecard kind {kind}")
    led = Ledger("scorecard", ledger_dir) if ledger_dir else Ledger("scorecard")
    return led.append({"id": new_id("s"), "kind": kind, "points": table[kind], "reason": reason, "ref": ref,
                       "category": "integrity" if kind in INTEGRITY else "risk" if kind in RISK else
                       "penalty" if table[kind] < 0 else "reward"}, now=now)


def totals(rows):
    pts = sum(r["points"] for r in rows)
    return {"points": pts,
            "rewards": sum(r["points"] for r in rows if r["points"] > 0),
            "penalties": sum(r["points"] for r in rows if r["points"] < 0),
            "integrity_violations": sum(1 for r in rows if r["kind"] in INTEGRITY),
            "risk_violations": sum(1 for r in rows if r["kind"] in RISK),
            "timestamp_errors": sum(1 for r in rows if r["kind"] == "timestamp_error"),
            "events": len(rows)}
