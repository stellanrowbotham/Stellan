"""Health checks: ledger integrity, accounting, config approval, data freshness, integrations, jobs."""
import os

from .ledger import Ledger, iso, parse_ts, verify_all
from .settings import approved_hash, config_hash

ENV_KEYS = ["TWELVEDATA_API_KEY", "ALPHAVANTAGE_API_KEY", "FINNHUB_API_KEY", "FRED_API_KEY", "COINGECKO_DEMO_API_KEY", "SEC_USER_AGENT"]


def source_status(settings, ledger_dir=None):
    """Latest known status per registry source (from source_checks), merged with static registry facts."""
    kw = {"directory": ledger_dir} if ledger_dir else {}
    last, last_ok = {}, {}
    for c in Ledger("source_checks", **kw).read():
        last[c["source_id"]] = c
        if c["status"] in ("ok", "partial"):
            last_ok[c["source_id"]] = c["at"]
    out = []
    for s in settings.sources:
        c = last.get(s["id"])
        if c:
            status = c["status"]
        elif s["integration"] in ("headline-only", "manual"):
            status = s["integration"]
        elif s["env_key"] and not os.environ.get(s["env_key"]):
            status = "needs-key"
        elif s["provider"]:
            status = "not-yet-checked"
        else:
            status = "not-integrated"
        out.append({**s, "status": status, "last_check": c["at"] if c else None, "last_success": last_ok.get(s["id"]),
                    "last_error": c["error"] if c else ""})
    return out


def run(settings, broker, now, ledger_dir=None):
    kw = {"directory": ledger_dir} if ledger_dir else {}
    issues = []
    for p in verify_all(ledger_dir) if ledger_dir else verify_all():
        issues.append({"level": "error", "what": "ledger tampering/corruption", "detail": p})
    if approved_hash(settings.config_dir) != config_hash(settings.config_dir):
        issues.append({"level": "error", "what": "config not approved", "detail": "settings/universe changed without Stellan's approval: trading locked"})
    ok, lhs, rhs = broker.portfolio().reconcile()
    if not ok:
        issues.append({"level": "error", "what": "accounting", "detail": f"cash+basis {lhs:.4f} vs start+realized {rhs:.4f}"})
    missing = [k for k in ENV_KEYS if not os.environ.get(k)]
    if missing:
        issues.append({"level": "warn", "what": "integrations not configured", "detail": "missing env: " + ", ".join(missing)})
    vals = Ledger("valuations", **kw).read()
    if vals and vals[-1].get("stale_marks"):
        issues.append({"level": "warn", "what": "stale prices", "detail": "open positions priced with >24h-old data: " + ", ".join(vals[-1]["stale_marks"])})
    blocked = [s["id"] for s in source_status(settings, ledger_dir) if s["status"] == "blocked-by-network"]
    if blocked:
        issues.append({"level": "error", "what": "network policy", "detail": "blocked: " + ", ".join(blocked)})
    runs = [h for h in Ledger("health", **kw).read() if h.get("what") == "run"]
    if runs:
        gap = (now - parse_ts(runs[-1]["at"])).total_seconds() / 3600
        if gap > 30:
            issues.append({"level": "warn", "what": "scheduled jobs", "detail": f"last recorded run was {gap:.0f} hours ago"})
    return issues


def record_run(job, now, ledger_dir=None, detail=""):
    kw = {"directory": ledger_dir} if ledger_dir else {}
    return Ledger("health", **kw).append({"level": "info", "what": "run", "job": job, "at": iso(now), "detail": detail}, now=now)
