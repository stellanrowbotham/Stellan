"""Append-only, hash-chained JSON-lines storage.

Every record gets `seq`, `recorded_at`, `prev_hash` and `hash`. Changing or deleting an old line
breaks the chain, and `verify()` reports exactly where. Records are never edited in place:
updates (closing a trade, scoring a forecast) are new records that reference the original id.
This is how "old predictions are never overwritten after the outcome is known" is enforced.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

PKG = Path(__file__).resolve().parent
LEDGER_DIR = PKG / "ledger"
GENESIS = "0" * 64


def utcnow():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_ts(s):
    if s is None:
        return None
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _digest(record):
    body = {k: v for k, v in record.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


class Ledger:
    def __init__(self, name, directory=LEDGER_DIR):
        self.path = Path(directory) / f"{name}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read(self):
        if not self.path.exists():
            return []
        return [json.loads(l) for l in self.path.read_text().splitlines() if l.strip()]

    def _tail(self):
        rows = self.read()
        return (rows[-1]["seq"], rows[-1]["hash"]) if rows else (0, GENESIS)

    def append(self, record, now=None):
        if "seq" in record or "hash" in record:
            raise ValueError("seq/hash are assigned by the ledger")
        seq, prev = self._tail()
        rec = dict(record)
        rec["seq"] = seq + 1
        rec["recorded_at"] = iso(now or utcnow())
        rec["prev_hash"] = prev
        rec["hash"] = _digest(rec)
        with self.path.open("a") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec

    def verify(self):
        """Return a list of problems (empty if the chain is intact)."""
        problems, prev = [], GENESIS
        for i, rec in enumerate(self.read(), 1):
            if rec.get("seq") != i:
                problems.append(f"{self.path.name}: line {i} has seq {rec.get('seq')}")
            if rec.get("prev_hash") != prev:
                problems.append(f"{self.path.name}: line {i} prev_hash mismatch (a line was removed or reordered)")
            if _digest(rec) != rec.get("hash"):
                problems.append(f"{self.path.name}: line {i} content changed after it was written")
            prev = rec.get("hash")
        return problems


LEDGER_NAMES = ("quotes", "research", "forecasts", "forecast_scores", "orders", "fills", "trades",
                "reviews", "scorecard", "evaluations", "level_events", "health", "source_checks", "watchlist",
                "valuations", "reports", "experiments")


def verify_all(directory=LEDGER_DIR):
    out = []
    for n in LEDGER_NAMES:
        out += Ledger(n, directory).verify()
    return out
