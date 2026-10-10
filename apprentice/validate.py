"""Data validation and look-ahead protection."""
from datetime import timedelta

from .ledger import parse_ts

MAX_FUTURE_SKEW = timedelta(minutes=5)
MAX_SPREAD = {"crypto": 0.02, "stock": 0.01, "etf": 0.01}
MAX_CROSS_SOURCE_GAP = 0.02


def quote_problems(q, now):
    """Problems that make a quote unusable. Empty list = usable."""
    p = []
    price = q.get("price")
    bid, ask = q.get("bid"), q.get("ask")
    if price is None and (bid is None or ask is None):
        p.append("no price")
    for name, v in (("price", price), ("bid", bid), ("ask", ask)):
        if v is not None and not v > 0:
            p.append(f"{name} not positive")
    if bid is not None and ask is not None:
        if bid > ask:
            p.append("bid above ask")
        elif bid > 0 and (ask - bid) / ((ask + bid) / 2) > MAX_SPREAD.get(q.get("asset_type"), 0.01):
            p.append(f"spread {(ask - bid) / ((ask + bid) / 2):.2%} too wide")
    for f in ("data_ts", "observed_at"):
        t = parse_ts(q.get(f))
        if t and t > now + MAX_FUTURE_SKEW:
            p.append(f"{f} is in the future (timestamp error)")
    if not q.get("observed_at"):
        p.append("missing observed_at")
    return p


def age_minutes(q, now):
    """Age of the quote's data. Uses data_ts when the provider gives one, otherwise observed_at."""
    t = parse_ts(q.get("data_ts")) or parse_ts(q.get("observed_at"))
    return (now - t).total_seconds() / 60.0


def is_fresh(q, now, max_minutes):
    return age_minutes(q, now) <= max_minutes


def cross_source_conflicts(quotes):
    """Same symbol, different providers, observed within 15 minutes, prices >2% apart."""
    out = []
    by_sym = {}
    for q in quotes:
        by_sym.setdefault(q["symbol"], []).append(q)
    for sym, qs in by_sym.items():
        for i, a in enumerate(qs):
            for b in qs[i + 1:]:
                if a["provider"] == b["provider"]:
                    continue
                ta, tb = parse_ts(a["observed_at"]), parse_ts(b["observed_at"])
                if abs((ta - tb).total_seconds()) > 900:
                    continue
                pa, pb = a.get("price") or a.get("ask"), b.get("price") or b.get("ask")
                if pa and pb and abs(pa - pb) / min(pa, pb) > MAX_CROSS_SOURCE_GAP:
                    out.append({"symbol": sym, "a": a["id"], "b": b["id"], "gap": abs(pa - pb) / min(pa, pb)})
    return out


def lookahead_violations(decided_at, evidence):
    """Any evidence observed, published or recorded after the decision time is look-ahead."""
    d = parse_ts(decided_at)
    bad = []
    for e in evidence:
        for f in ("observed_at", "published_at", "recorded_at", "data_ts"):
            t = parse_ts(e.get(f))
            if t and t > d + timedelta(seconds=1):
                bad.append(f"{e.get('id')}: {f} {e.get(f)} is after decision {decided_at}")
                break
    return bad
