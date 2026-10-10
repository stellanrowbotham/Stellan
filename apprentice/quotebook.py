"""Point-in-time lookups over stored data. Everything takes `now` and ignores records observed
after it, so the same code works for live runs and replays without look-ahead."""
from datetime import timedelta

from .ledger import Ledger, parse_ts
from .validate import age_minutes, quote_problems


class QuoteBook:
    def __init__(self, ledger_dir=None):
        kw = {"directory": ledger_dir} if ledger_dir else {}
        self.quotes = Ledger("quotes", **kw).read()
        self.research = Ledger("research", **kw).read()

    def latest(self, symbol, now, providers=None, valid_only=True):
        best = None
        for q in self.quotes:
            if q["symbol"] != symbol or parse_ts(q["observed_at"]) > now:
                continue
            if providers and q["provider"] not in providers:
                continue
            if valid_only and quote_problems(q, now):
                continue
            if best is None or (parse_ts(q.get("data_ts") or q["observed_at"]), q["seq"]) > (
                    parse_ts(best.get("data_ts") or best["observed_at"]), best["seq"]):
                best = q
        return best

    def first_after(self, symbol, t, now, tolerance_minutes):
        """First valid quote whose data time is at/after t (and within tolerance), observed by now."""
        cands = []
        for q in self.quotes:
            if q["symbol"] != symbol or parse_ts(q["observed_at"]) > now or quote_problems(q, now):
                continue
            dt = parse_ts(q.get("data_ts") or q["observed_at"])
            if t <= dt <= t + timedelta(minutes=tolerance_minutes):
                cands.append((dt, q["seq"], q))
        return min(cands)[2] if cands else None

    def usdcad(self, now, max_age_days=5):
        best = None
        for r in self.research:
            if r.get("kind") == "macro" and r.get("series") == "FXUSDCAD" and parse_ts(r["observed_at"]) <= now:
                if best is None or r["data_date"] >= best["data_date"]:
                    best = r
        if best and (now.date() - parse_ts(best["data_date"] + "T00:00:00+00:00").date()).days <= max_age_days:
            return best["value"]
        return None

    def mark(self, symbol, now):
        """CAD-agnostic unit mark: bid when quoted, else last price. Returns (price, quote) or (None, None)."""
        q = self.latest(symbol, now)
        if not q:
            return None, None
        return (q["bid"] if q.get("bid") is not None else q["price"]), q
