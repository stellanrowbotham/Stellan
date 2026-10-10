"""Forecasts are recorded before the outcome and scored later with the Brier score.

Brier = (probability - outcome)^2, where outcome is 1 if the predicted direction happened.
0 is perfect, 0.25 is what always saying 50% gets you, and lower is better."""
from datetime import timedelta

from . import scorecard
from .ledger import Ledger, iso, new_id, parse_ts
from .quotebook import QuoteBook
from .validate import lookahead_violations

REQUIRED = ("symbol", "direction", "probability", "horizon_end", "reference_quote_id", "rationale", "evidence_ids", "made_at")
HORIZONS = {"1h": timedelta(hours=1), "4h": timedelta(hours=4), "1d": timedelta(days=1), "5d": timedelta(days=5),
            "20d": timedelta(days=28), "60d": timedelta(days=90)}


def add(settings, f, now, ledger_dir=None):
    kw = {"directory": ledger_dir} if ledger_dir else {}
    f = dict(f)
    f.setdefault("made_at", iso(now))
    if "horizon" in f and "horizon_end" not in f and f["horizon"] in HORIZONS:
        f["horizon_end"] = iso(parse_ts(f["made_at"]) + HORIZONS[f["horizon"]])
    problems = [f"missing {k}" for k in REQUIRED if f.get(k) in (None, "", [])]
    if settings.asset(f.get("symbol")) is None:
        problems.append(f"{f.get('symbol')} not in approved universe")
    if f.get("direction") not in ("up", "down"):
        problems.append("direction must be up or down")
    lo, hi = settings["forecasts"]["min_probability"], settings["forecasts"]["max_probability"]
    if not isinstance(f.get("probability"), (int, float)) or not lo <= f["probability"] <= hi:
        problems.append(f"probability must be between {lo} and {hi}")
    ev_ids = list(f.get("evidence_ids") or []) + ([f["reference_quote_id"]] if f.get("reference_quote_id") else [])
    pool = {r["id"]: r for n in ("research", "quotes") for r in Ledger(n, **kw).read() if "id" in r}
    missing = [i for i in ev_ids if i not in pool]
    if missing:
        problems.append(f"evidence not in ledger: {missing}")
    la = lookahead_violations(f["made_at"], [pool[i] for i in ev_ids if i in pool])
    problems += la
    if f.get("horizon_end") and parse_ts(f["horizon_end"]) <= parse_ts(f["made_at"]):
        problems.append("horizon_end must be after made_at")
    if problems:
        kind = "timestamp_error" if la else "fabricated_or_unsourced_fact" if missing else "missing_required_disclosure"
        scorecard.award(settings, kind, "forecast rejected: " + "; ".join(problems), None, ledger_dir, now)
        return None, problems
    ref = pool[f["reference_quote_id"]]
    f["reference_price"] = ref.get("price") if ref.get("price") is not None else (ref["bid"] + ref["ask"]) / 2
    f["id"] = new_id("fc")
    f["complete"] = True
    return Ledger("forecasts", **kw).append(f, now=now), []


def score_due(settings, now, ledger_dir=None):
    kw = {"directory": ledger_dir} if ledger_dir else {}
    book = QuoteBook(ledger_dir)
    scored_led = Ledger("forecast_scores", **kw)
    done = {s["forecast_id"] for s in scored_led.read()}
    out = []
    for f in Ledger("forecasts", **kw).read():
        if f["id"] in done or parse_ts(f["horizon_end"]) > now:
            continue
        a = settings.asset(f["symbol"])
        tol = settings["forecasts"]["score_tolerance_minutes"]["crypto" if a["asset_type"] == "crypto" else "stock"]
        q = book.first_after(f["symbol"], parse_ts(f["horizon_end"]), now, tol)
        if q is None:
            if now > parse_ts(f["horizon_end"]) + timedelta(minutes=tol):
                out.append(scored_led.append({"forecast_id": f["id"], "status": "unscorable",
                                              "reason": "no valid price within tolerance after the horizon"}, now=now))
            continue
        px = q.get("price") if q.get("price") is not None else (q["bid"] + q["ask"]) / 2
        up = px > f["reference_price"]
        hit = (f["direction"] == "up" and up) or (f["direction"] == "down" and px < f["reference_price"])
        o = 1.0 if hit else 0.0
        out.append(scored_led.append({"forecast_id": f["id"], "status": "scored", "outcome_quote_id": q["id"],
                                      "outcome_price": px, "hit": hit, "brier": (f["probability"] - o) ** 2,
                                      "move_pct": px / f["reference_price"] - 1}, now=now))
    return out


def stats(forecasts, scores):
    by = {s["forecast_id"]: s for s in scores if s["status"] == "scored"}
    rows = [(f, by[f["id"]]) for f in forecasts if f["id"] in by]
    if not rows:
        return {"scored": 0, "pending": len(forecasts) - len(scores), "unscorable": sum(1 for s in scores if s["status"] == "unscorable")}
    briers = [s["brier"] for _, s in rows]
    buckets = {}
    for f, s in rows:
        b = min(int(f["probability"] * 10), 9) / 10
        k = f"{b:.1f}-{b + 0.1:.1f}"
        buckets.setdefault(k, []).append(s["hit"])
    return {"scored": len(rows), "pending": len(forecasts) - len(scores),
            "unscorable": sum(1 for s in scores if s["status"] == "unscorable"),
            "hit_rate": sum(s["hit"] for _, s in rows) / len(rows), "brier": sum(briers) / len(briers),
            "brier_last30": sum(briers[-30:]) / len(briers[-30:]),
            "calibration": {k: {"n": len(v), "hit_rate": sum(v) / len(v)} for k, v in sorted(buckets.items())}}
