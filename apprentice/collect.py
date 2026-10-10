"""Scheduled data collection. Writes what was actually retrieved, plus one source_checks record per
source so the registry always shows what works, what is blocked and what needs a key."""
import json
from datetime import timedelta

from .ledger import Ledger, iso, new_id
from .providers import sources as P
from .settings import PKG
from .validate import cross_source_conflicts, quote_problems

DEFAULT_WATCH = ["XIU", "XIC", "VFV", "XEQT", "RY", "TD", "ENB", "CNR", "SHOP", "ATD", "FTS", "BCE", "SPY", "QQQ"]


def watchlist(settings, broker, ledger_dir=None):
    kw = {"directory": ledger_dir} if ledger_dir else {}
    rows = Ledger("watchlist", **kw).read()
    current = set(DEFAULT_WATCH)
    for r in rows:  # replay add/remove events
        if r.get("action") == "add" and settings.asset(r["symbol"]):
            current.add(r["symbol"])
        elif r.get("action") == "remove":
            current.discard(r["symbol"])
    for b in settings["benchmarks"].values():
        current.add(b["symbol"])
    current |= {t["symbol"] for t in broker.trades().values() if t["status"] in ("open", "pending")}
    return sorted(s for s in current if settings.asset(s))


def _record(results, now, kw, scope):
    checks = Ledger("source_checks", **kw)
    for r in results:
        checks.append({"source_id": r.source_id, "status": r.status, "error": r.error[:500], "calls": r.calls,
                       "records": len(r.records), "scope": scope, "at": iso(now)}, now=now)


def run(settings, broker, now, scope=("crypto", "stocks", "macro", "news"), ledger_dir=None):
    kw = {"directory": ledger_dir} if ledger_dir else {}
    QL, RL, HL = Ledger("quotes", **kw), Ledger("research", **kw), Ledger("health", **kw)
    results, quotes = [], []
    wl = watchlist(settings, broker, ledger_dir)
    if "macro" in scope or "stocks" in scope:
        results.append(P.bank_of_canada())
    if "crypto" in scope:
        pairs = [a["symbol"] for a in settings.universe if a["asset_type"] == "crypto"]
        results.append(P.kraken(pairs))
        results.append(P.coingecko([a["coingecko_id"] for a in settings.universe if a.get("coingecko_id")]))
        if "macro" in scope:
            results.append(P.defillama())
    if "stocks" in scope:
        assets = [settings.asset(s) for s in wl if settings.asset(s)["asset_type"] != "crypto"]
        td = P.twelve_data_quotes(assets)
        results.append(td)
        got = {q["symbol"] for q in td.records}
        tsx_missing = [a for a in assets if a["exchange"] == "TSX" and a["symbol"] not in got]
        if tsx_missing:
            results.append(P.alpha_vantage_quotes(tsx_missing[:10]))
        results.append(P.finnhub_quotes([a for a in assets if a["exchange"] == "US"]))
    if "macro" in scope:
        results.append(P.fred())
        today = now.date()
        results.append(P.finnhub_earnings(today.isoformat(), (today + timedelta(days=7)).isoformat()))
        us = [s for s in wl if settings.asset(s)["exchange"] == "US" and settings.asset(s)["asset_type"] == "stock"]
        if us:
            results.append(P.sec_recent_filings(us))
    if "news" in scope:
        feeds = json.loads((PKG / "config" / "feeds.json").read_text())["feeds"]
        if "crypto" not in scope:
            feeds = [f for f in feeds if f["topic"] != "crypto"]
        if "stocks" not in scope and "macro" not in scope:
            feeds = [f for f in feeds if f["topic"] == "crypto"]
        news = P.rss(feeds)
        existing = [r for r in RL.read() if r.get("kind") == "headline"]
        fresh = P.dedupe_headlines([x for r in news for x in r.records], existing)
        keep = {id(x) for x in fresh}
        for r in news:
            r.records = [x for x in r.records if id(x) in keep]
        results += news

    stored = {"quotes": 0, "research": 0, "rejected": 0}
    for r in results:
        for rec in r.records:
            if "symbol" in rec and "provider" in rec:
                probs = quote_problems(rec, now)
                if probs:
                    stored["rejected"] += 1
                    HL.append({"level": "warn", "what": "invalid quote rejected", "detail": f"{rec['symbol']} from {rec['provider']}: {'; '.join(probs)}"}, now=now)
                    continue
                quotes.append(QL.append(rec, now=now))
                stored["quotes"] += 1
            else:
                RL.append(rec, now=now)
                stored["research"] += 1
    for c in cross_source_conflicts(quotes):
        HL.append({"level": "warn", "what": "conflicting prices", "detail": f"{c['symbol']}: {c['gap']:.1%} gap between {c['a']} and {c['b']}"}, now=now)
    _record(results, now, kw, ",".join(scope))
    summary = {r.source_id: r.status for r in results}
    HL.append({"level": "info" if any(r.ok for r in results) else "error", "what": "collect",
               "detail": f"scope={','.join(scope)} stored={stored} statuses={summary}"}, now=now)
    return {"stored": stored, "statuses": summary, "errors": {r.source_id: r.error for r in results if r.error}}
