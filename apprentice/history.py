"""Daily price history for the strategy lab, cached in apprentice/data/history/<SYMBOL>.json.

Sources (all real, all recorded with where they came from):
  US stocks/ETFs -> Twelve Data time_series (free plan: US only, 8 calls/min, 800/day)
  Crypto (CAD)   -> Kraken public OHLC (about 720 daily candles, no key)
  TSX            -> Alpha Vantage TIME_SERIES_DAILY (.TRT), when its 25/day budget allows
Bars are end-of-day and are never edited by hand. A refresh replaces the file with fresher bars."""
import json
import time as _time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from .ledger import iso, utcnow
from .providers.base import FetchError, budget_ok, env_key, http_json, redact, spend

DIR = Path(__file__).resolve().parent / "data" / "history"
LAB_EXTRA = [  # research-only proxies (not tradeable: not in the approved universe)
    {"symbol": "EWC", "exchange": "US", "asset_type": "etf", "currency": "USD", "note": "iShares MSCI Canada (US-listed proxy for Canadian stocks)"},
]


def path(symbol):
    return DIR / f"{symbol.replace('/', '_')}.json"


def load(symbol):
    p = path(symbol)
    return json.loads(p.read_text()) if p.exists() else None


def _save(symbol, bars, source, note=""):
    DIR.mkdir(parents=True, exist_ok=True)
    doc = {"symbol": symbol, "source": source, "fetched_at": iso(utcnow()), "note": note, "bars": bars}
    path(symbol).write_text(json.dumps(doc))
    return doc


def twelve_data(symbol, outputsize=5000):
    key = env_key("TWELVEDATA_API_KEY")
    if not key:
        raise FetchError("needs-key", "set TWELVEDATA_API_KEY")
    if not budget_ok("twelve_data", 800):
        raise FetchError("rate-limited", "twelve data daily budget used")
    j = http_json("https://api.twelvedata.com/time_series?" + urllib.parse.urlencode(
        {"symbol": symbol, "interval": "1day", "outputsize": outputsize, "apikey": key}), timeout=40)
    spend("twelve_data")
    if j.get("status") == "error":
        raise FetchError("bad-response", redact(str(j.get("message")))[:200])
    bars = [{"date": v["datetime"][:10], "open": float(v["open"]), "high": float(v["high"]), "low": float(v["low"]),
             "close": float(v["close"]), "volume": float(v.get("volume") or 0)} for v in reversed(j.get("values", []))]
    return _save(symbol, bars, "twelve_data")


def kraken(pair):
    from .providers.sources import _kraken_norm
    meta = http_json("https://api.kraken.com/0/public/AssetPairs")
    key = next((k for k, v in meta["result"].items() if _kraken_norm(v.get("wsname") or v.get("altname") or "") == _kraken_norm(pair)), None)
    if not key:
        raise FetchError("bad-response", f"{pair} not listed on Kraken")
    j = http_json(f"https://api.kraken.com/0/public/OHLC?pair={key}&interval=1440")
    if j.get("error"):
        raise FetchError("bad-response", str(j["error"]))
    rows = next(v for k, v in j["result"].items() if k != "last")
    bars = [{"date": datetime.fromtimestamp(r[0], tz=timezone.utc).date().isoformat(), "open": float(r[1]), "high": float(r[2]),
             "low": float(r[3]), "close": float(r[4]), "volume": float(r[6])} for r in rows]
    return _save(pair, bars[:-1], "kraken", "last (unfinished) daily candle dropped")


def alpha_vantage(asset):
    key = env_key("ALPHAVANTAGE_API_KEY")
    if not key:
        raise FetchError("needs-key", "set ALPHAVANTAGE_API_KEY")
    if not budget_ok("alpha_vantage", 25):
        raise FetchError("rate-limited", "alpha vantage daily budget used")
    sym = asset["symbol"].replace(".", "-") + ".TRT"
    j = http_json(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=compact&symbol={sym}&apikey={key}")
    spend("alpha_vantage")
    ts = j.get("Time Series (Daily)")
    if not ts:
        raise FetchError("rate-limited" if "rate limit" in str(j).lower() else "bad-response", redact(str(j))[:200])
    bars = [{"date": d, "open": float(v["1. open"]), "high": float(v["2. high"]), "low": float(v["3. low"]),
             "close": float(v["4. close"]), "volume": float(v["5. volume"])} for d, v in sorted(ts.items())]
    return _save(asset["symbol"], bars, "alpha_vantage", "compact (last ~100 days) on the free plan")


def refresh(settings, scope=("us", "crypto", "tsx"), max_age_hours=20, pause=8.0, log=print):
    """Fetch history for every approved asset (plus lab proxies) whose cache is older than max_age_hours."""
    done, failed = [], []
    assets = list(settings.universe) + LAB_EXTRA
    for a in assets:
        kind = "crypto" if a["asset_type"] == "crypto" else ("tsx" if a["exchange"] == "TSX" else "us")
        if kind not in scope:
            continue
        cur = load(a["symbol"])
        if cur and (utcnow() - datetime.fromisoformat(cur["fetched_at"].replace("Z", "+00:00"))).total_seconds() < max_age_hours * 3600:
            continue
        try:
            if kind == "us":
                doc = twelve_data(a["symbol"])
                _time.sleep(pause)  # free plan: 8 requests per minute
            elif kind == "crypto":
                doc = kraken(a["symbol"])
            else:
                doc = alpha_vantage(a)
                _time.sleep(1.5)
            done.append((a["symbol"], len(doc["bars"])))
            log(f"ok {a['symbol']}: {len(doc['bars'])} bars from {doc['source']}")
        except FetchError as e:
            failed.append((a["symbol"], e.status, str(e)[:120]))
            log(f"skip {a['symbol']}: {e.status} {str(e)[:120]}")
            if e.status == "rate-limited" and kind == "tsx":
                scope = tuple(s for s in scope if s != "tsx")
    return {"fetched": done, "failed": failed}
