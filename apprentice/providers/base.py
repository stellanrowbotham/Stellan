import json
import os
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..ledger import iso, new_id, utcnow

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
USER_AGENT = "StellanInvestingApprentice/0.1 (personal research; simulation only)"


@dataclass
class ProviderResult:
    source_id: str
    status: str  # ok | partial | needs-key | blocked-by-network | rate-limited | http-error | bad-response | not-integrated
    records: list = field(default_factory=list)
    error: str = ""
    calls: int = 0

    @property
    def ok(self):
        return self.status in ("ok", "partial")


class FetchError(Exception):
    def __init__(self, status, msg):
        super().__init__(msg)
        self.status = status


def _ssl_context():
    ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if Path("/root/.ccr/ca-bundle.crt").exists() else None)
    return ssl.create_default_context(cafile=ca) if ca else ssl.create_default_context()


def http_get(url, headers=None, timeout=20):
    h = {"User-Agent": os.environ.get("SEC_USER_AGENT") if "sec.gov" in url and os.environ.get("SEC_USER_AGENT") else USER_AGENT,
         "Accept": "application/json, application/xml, text/xml, */*"}
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        status = "rate-limited" if e.code == 429 else "http-error"
        raise FetchError(status, f"HTTP {e.code} from {url.split('?')[0]}")
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "403" in reason or "Tunnel connection failed" in reason or "CONNECT" in reason:
            raise FetchError("blocked-by-network", f"network policy blocked {url.split('/')[2]} ({reason})")
        raise FetchError("http-error", f"{url.split('/')[2]}: {reason}")
    except OSError as e:
        msg = str(e)
        if "403" in msg or "Tunnel" in msg:
            raise FetchError("blocked-by-network", f"network policy blocked {url.split('/')[2]} ({msg})")
        raise FetchError("http-error", f"{url.split('/')[2]}: {msg}")


def http_json(url, headers=None, timeout=20):
    raw = http_get(url, headers, timeout)
    try:
        return json.loads(raw)
    except ValueError:
        raise FetchError("bad-response", f"non-JSON response from {url.split('?')[0]}")


def env_key(name):
    v = os.environ.get(name, "").strip()
    return v or None


# ---------------------------------------------------------------- daily call budgets
def _usage_path():
    STATE_DIR.mkdir(exist_ok=True)
    return STATE_DIR / "usage.json"


def budget_ok(provider, daily_limit, n=1):
    p = _usage_path()
    today = utcnow().date().isoformat()
    data = json.loads(p.read_text()) if p.exists() else {}
    used = data.get(today, {}).get(provider, 0)
    return used + n <= daily_limit


def spend(provider, n=1):
    p = _usage_path()
    today = utcnow().date().isoformat()
    data = json.loads(p.read_text()) if p.exists() else {}
    data = {today: data.get(today, {})}  # keep only today
    data[today][provider] = data[today].get(provider, 0) + n
    p.write_text(json.dumps(data, indent=1))


def quote_record(*, symbol, exchange, asset_type, currency, provider, source_id, price=None, bid=None, ask=None,
                 data_ts=None, observed_at=None, extra=None):
    rec = {
        "id": new_id("q"),
        "symbol": symbol, "exchange": exchange, "asset_type": asset_type, "currency": currency,
        "price": price, "bid": bid, "ask": ask,
        "spread_source": "quoted" if (bid is not None and ask is not None) else "none",
        "data_ts": data_ts, "observed_at": observed_at or iso(utcnow()),
        "provider": provider, "source_id": source_id,
    }
    if extra:
        rec.update(extra)
    return rec


def ts_from_unix(t):
    return iso(datetime.fromtimestamp(int(t), tz=timezone.utc)) if t else None
