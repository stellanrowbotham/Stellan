"""Research records: headlines, filings, macro data and the agent's own notes.

Every record says what kind of claim it is (fact / estimate / opinion / ai_interpretation), where it
came from, when it was published and when it was observed. Syndicated copies share an origin_id
and never count as independent confirmation."""
from . import scorecard
from .ledger import Ledger, iso, new_id, parse_ts
from .validate import MAX_FUTURE_SKEW

CLAIM_TYPES = {"fact", "estimate", "opinion", "ai_interpretation"}
TIER_WEIGHT = {"A": 1.0, "B": 0.85, "C": 0.7, "D": 0.3}


def validate_note(settings, rec, known, now):
    """Problems with an agent-written research note (empty list = OK)."""
    p = []
    for f in ("kind", "title", "claim_type"):
        if not rec.get(f):
            p.append(f"missing {f}")
    if rec.get("claim_type") and rec["claim_type"] not in CLAIM_TYPES:
        p.append(f"claim_type must be one of {sorted(CLAIM_TYPES)}")
    if rec.get("claim_type") in ("fact", "estimate"):
        if not (rec.get("url") or rec.get("based_on")):
            p.append("facts and estimates need a url or based_on evidence ids")
    if rec.get("url") and not rec.get("source_id") and not rec.get("publisher"):
        p.append("web evidence needs source_id or publisher")
    if rec.get("source_id") and rec["source_id"] not in {s["id"] for s in settings.sources} | {"web"}:
        p.append(f"unknown source_id {rec['source_id']} (use 'web' plus publisher for other sites)")
    missing = [i for i in rec.get("based_on", []) if i not in known]
    if missing:
        p.append(f"based_on ids not in the ledger: {missing}")
    pub = parse_ts(rec.get("published_at")) if rec.get("published_at") else None
    if pub and pub > now + MAX_FUTURE_SKEW:
        p.append("published_at is in the future")
    if rec.get("url") and not rec.get("published_at") and not rec.get("published_unknown_reason"):
        p.append("give published_at, or published_unknown_reason")
    return p


def add_notes(settings, notes, now, ledger_dir=None):
    kw = {"directory": ledger_dir} if ledger_dir else {}
    led = Ledger("research", **kw)
    known = {r["id"] for n in ("research", "quotes", "forecasts") for r in Ledger(n, **kw).read() if "id" in r}
    added, rejected = [], []
    for n in notes:
        rec = dict(n)
        rec.setdefault("id", new_id("r"))
        rec.setdefault("observed_at", iso(now))
        rec.setdefault("origin_id", rec.get("origin_id") or rec["id"])
        probs = validate_note(settings, rec, known, now)
        if probs:
            rejected.append({"title": rec.get("title"), "problems": probs})
            kind = "timestamp_error" if any("future" in x for x in probs) else (
                "fabricated_or_unsourced_fact" if any("not in the ledger" in x or "need a url" in x for x in probs)
                else "missing_required_disclosure")
            scorecard.award(settings, kind, f"research note rejected: {'; '.join(probs)}", rec["id"], ledger_dir, now)
            continue
        added.append(led.append(rec, now=now))
        known.add(rec["id"])
    return added, rejected


def source_tier(settings, rec):
    by_id = {s["id"]: s for s in settings.sources}
    s = by_id.get(rec.get("source_id"))
    if s:
        return s["tier"]
    return rec.get("tier_override") or "D"


def independence(settings, evidence):
    """Distinct origins among evidence (syndicated copies collapse) and the best tier seen."""
    origins, tiers = set(), []
    for e in evidence:
        if e.get("kind") in ("headline", "filing", "macro", "note", "event", "crypto_market", "chain_tvl") or e.get("url"):
            origins.add(e.get("origin_id") or e.get("id"))
            tiers.append(source_tier(settings, e))
        elif e.get("provider"):  # a quote
            origins.add(f"quote:{e['provider']}")
            tiers.append(source_tier(settings, e))
    return len(origins), sorted(tiers)
