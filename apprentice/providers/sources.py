"""Concrete provider adapters. Keys come from environment variables only and are never logged
(URLs are cut at '?' before they go into any error message)."""
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, time, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

from ..ledger import iso, new_id, utcnow
from .base import FetchError, ProviderResult, budget_ok, env_key, http_get, http_json, quote_record, spend, ts_from_unix

TORONTO = ZoneInfo("America/Toronto")


def _fail(source_id, e, calls=0):
    return ProviderResult(source_id, e.status if isinstance(e, FetchError) else "bad-response", [], str(e), calls)


# ---------------------------------------------------------------- Bank of Canada (FX + policy rate)
BOC_SERIES = {"FXUSDCAD": "USD/CAD daily exchange rate", "V39079": "Target for the overnight rate (unverified series id)"}


def bank_of_canada(series=("FXUSDCAD", "V39079")):
    recs, calls = [], 0
    try:
        for s in series:
            j = http_json(f"https://www.bankofcanada.ca/valet/observations/{s}/json?recent=1")
            calls += 1
            obs = (j.get("observations") or [])
            if not obs or s not in obs[-1]:
                continue
            o = obs[-1]
            recs.append({"id": new_id("m"), "kind": "macro", "series": s, "label": BOC_SERIES.get(s, s),
                         "value": float(o[s]["v"]), "data_date": o["d"], "observed_at": iso(utcnow()),
                         "source_id": "bank_of_canada_valet", "url": f"https://www.bankofcanada.ca/valet/observations/{s}/json"})
    except FetchError as e:
        return _fail("bank_of_canada_valet", e, calls)
    return ProviderResult("bank_of_canada_valet", "ok" if recs else "bad-response", recs, "" if recs else "no observations", calls)


# ---------------------------------------------------------------- Kraken (tradable crypto bid/ask)
def kraken(pairs):
    pairs = list(pairs)
    if not pairs:
        return ProviderResult("kraken_market_data", "ok")
    q = ",".join(pairs)
    try:
        meta = http_json(f"https://api.kraken.com/0/public/AssetPairs?pair={q}")
        tick = http_json(f"https://api.kraken.com/0/public/Ticker?pair={q}")
    except FetchError as e:
        return _fail("kraken_market_data", e, 2)
    if meta.get("error") or tick.get("error"):
        # Kraken rejects the whole request if one pair is unknown; retry pair by pair.
        if len(pairs) > 1:
            out = ProviderResult("kraken_market_data", "ok", [], "", 2)
            errs = []
            for p in pairs:
                r = kraken([p])
                out.calls += r.calls
                out.records += r.records
                if not r.ok:
                    errs.append(f"{p}: {r.error}")
            out.status = "ok" if not errs else ("partial" if out.records else "bad-response")
            out.error = "; ".join(errs)
            return out
        return ProviderResult("kraken_market_data", "bad-response", [], f"{pairs[0]}: {meta.get('error') or tick.get('error')}", 2)
    alt = {k: v.get("altname") for k, v in meta.get("result", {}).items()}
    now = iso(utcnow())
    recs = []
    for key, t in tick.get("result", {}).items():
        sym = alt.get(key, key)
        recs.append(quote_record(symbol=sym, exchange="KRAKEN", asset_type="crypto", currency="CAD",
                                 provider="kraken", source_id="kraken_market_data",
                                 price=float(t["c"][0]), bid=float(t["b"][0]), ask=float(t["a"][0]),
                                 data_ts=now, observed_at=now,
                                 extra={"volume_24h": float(t["v"][1]), "data_ts_note": "Kraken ticker has no timestamp; observed_at used"}))
    missing = set(pairs) - {r["symbol"] for r in recs}
    return ProviderResult("kraken_market_data", "ok" if not missing else "partial", recs,
                          f"missing pairs: {sorted(missing)}" if missing else "", 2)


# ---------------------------------------------------------------- CoinGecko (market context, not fills)
def coingecko(ids):
    key = env_key("COINGECKO_DEMO_API_KEY")
    if not key:
        return ProviderResult("coingecko", "needs-key", [], "set COINGECKO_DEMO_API_KEY (free Demo plan)")
    url = ("https://api.coingecko.com/api/v3/simple/price?ids=" + ",".join(ids) +
           "&vs_currencies=cad&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true")
    try:
        j = http_json(url, headers={"x-cg-demo-api-key": key})
    except FetchError as e:
        return _fail("coingecko", e, 1)
    now = iso(utcnow())
    recs = [{"id": new_id("m"), "kind": "crypto_market", "coingecko_id": cid, "price_cad": v.get("cad"),
             "market_cap_cad": v.get("cad_market_cap"), "volume_24h_cad": v.get("cad_24h_vol"),
             "change_24h_pct": v.get("cad_24h_change"), "data_ts": ts_from_unix(v.get("last_updated_at")),
             "observed_at": now, "source_id": "coingecko", "url": "https://www.coingecko.com/en/coins/" + cid}
            for cid, v in j.items()]
    return ProviderResult("coingecko", "ok", recs, "", 1)


# ---------------------------------------------------------------- DefiLlama (no key)
def defillama():
    try:
        chains = http_json("https://api.llama.fi/v2/chains")
    except FetchError as e:
        return _fail("defillama", e, 1)
    now = iso(utcnow())
    top = sorted(chains, key=lambda c: c.get("tvl") or 0, reverse=True)[:10]
    recs = [{"id": new_id("m"), "kind": "chain_tvl", "chain": c.get("name"), "tvl_usd": c.get("tvl"),
             "observed_at": now, "data_ts": now, "source_id": "defillama", "url": "https://defillama.com/chains"} for c in top]
    return ProviderResult("defillama", "ok", recs, "", 1)


# ---------------------------------------------------------------- Stock quotes
def _av_symbol(asset):
    s = asset["symbol"]
    return s.replace(".", "-") + ".TRT" if asset["exchange"] == "TSX" else s.replace(".", "-")


def alpha_vantage_quotes(assets, daily_limit=25):
    key = env_key("ALPHAVANTAGE_API_KEY")
    if not key:
        return ProviderResult("alpha_vantage", "needs-key", [], "set ALPHAVANTAGE_API_KEY (free)")
    out = ProviderResult("alpha_vantage", "ok")
    errs = []
    for a in assets:
        if not budget_ok("alpha_vantage", daily_limit):
            errs.append("daily budget used up")
            break
        try:
            j = http_json("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" +
                          urllib.parse.quote(_av_symbol(a)) + "&apikey=" + key)
        except FetchError as e:
            errs.append(f"{a['symbol']}: {e}")
            if e.status == "blocked-by-network":
                out.status = "blocked-by-network"
                break
            continue
        finally:
            spend("alpha_vantage")
            out.calls += 1
        g = j.get("Global Quote") or {}
        if not g.get("05. price"):
            errs.append(f"{a['symbol']}: {(j.get('Note') or j.get('Information') or 'empty quote')[:120]}")
            continue
        day = datetime.fromisoformat(g["07. latest trading day"]).date()
        close_ts = iso(datetime.combine(day, time(16, 0), TORONTO))
        out.records.append(quote_record(symbol=a["symbol"], exchange=a["exchange"], asset_type=a["asset_type"],
                                        currency=a["currency"], provider="alpha_vantage", source_id="alpha_vantage",
                                        price=float(g["05. price"]), data_ts=close_ts,
                                        extra={"data_ts_note": "latest trading day at 16:00 ET (end-of-day quote)",
                                               "prev_close": float(g.get("08. previous close") or 0) or None,
                                               "volume": int(g.get("06. volume") or 0)}))
    if errs and out.status == "ok":
        out.status = "partial" if out.records else "bad-response"
    out.error = "; ".join(errs[:8])
    return out


def twelve_data_quotes(assets, daily_limit=800):
    key = env_key("TWELVEDATA_API_KEY")
    if not key:
        return ProviderResult("twelve_data", "needs-key", [], "set TWELVEDATA_API_KEY (free)")
    out = ProviderResult("twelve_data", "ok")
    errs = []
    for a in assets:
        if not budget_ok("twelve_data", daily_limit):
            errs.append("daily budget used up")
            break
        params = {"symbol": a["symbol"], "apikey": key}
        if a["exchange"] == "TSX":
            params["exchange"] = "TSX"
        try:
            j = http_json("https://api.twelvedata.com/quote?" + urllib.parse.urlencode(params))
        except FetchError as e:
            errs.append(f"{a['symbol']}: {e}")
            if e.status == "blocked-by-network":
                out.status = "blocked-by-network"
                break
            continue
        finally:
            spend("twelve_data")
            out.calls += 1
        if j.get("status") == "error" or "close" not in j:
            errs.append(f"{a['symbol']}: {str(j.get('message', 'no data'))[:120]}")
            continue
        out.records.append(quote_record(symbol=a["symbol"], exchange=a["exchange"], asset_type=a["asset_type"],
                                        currency=a["currency"], provider="twelve_data", source_id="twelve_data",
                                        price=float(j["close"]), data_ts=ts_from_unix(j.get("last_quote_at") or j.get("timestamp")),
                                        extra={"is_market_open": j.get("is_market_open"),
                                               "prev_close": float(j["previous_close"]) if j.get("previous_close") else None,
                                               "volume": int(float(j.get("volume") or 0))}))
    if errs and out.status == "ok":
        out.status = "partial" if out.records else "bad-response"
    out.error = "; ".join(errs[:8])
    return out


def twelve_data_history(asset, days=120):
    key = env_key("TWELVEDATA_API_KEY")
    if not key:
        return ProviderResult("twelve_data", "needs-key", [], "set TWELVEDATA_API_KEY (free)")
    params = {"symbol": asset["symbol"], "interval": "1day", "outputsize": days, "apikey": key}
    if asset["exchange"] == "TSX":
        params["exchange"] = "TSX"
    try:
        j = http_json("https://api.twelvedata.com/time_series?" + urllib.parse.urlencode(params))
        spend("twelve_data")
    except FetchError as e:
        return _fail("twelve_data", e, 1)
    if j.get("status") == "error":
        return ProviderResult("twelve_data", "bad-response", [], str(j.get("message"))[:160], 1)
    bars = [{"date": v["datetime"], "open": float(v["open"]), "high": float(v["high"]), "low": float(v["low"]),
             "close": float(v["close"]), "volume": int(float(v.get("volume") or 0))} for v in reversed(j.get("values", []))]
    return ProviderResult("twelve_data", "ok", [{"id": new_id("h"), "kind": "history", "symbol": asset["symbol"],
                                                  "bars": bars, "observed_at": iso(utcnow()), "source_id": "twelve_data"}], "", 1)


def finnhub_quotes(assets):
    key = env_key("FINNHUB_API_KEY")
    if not key:
        return ProviderResult("finnhub", "needs-key", [], "set FINNHUB_API_KEY (free)")
    out = ProviderResult("finnhub", "ok")
    errs = []
    for a in assets:
        if a["exchange"] != "US":
            continue  # free tier: US only
        try:
            j = http_json("https://finnhub.io/api/v1/quote?symbol=" + urllib.parse.quote(a["symbol"]) + "&token=" + key)
            out.calls += 1
        except FetchError as e:
            errs.append(f"{a['symbol']}: {e}")
            if e.status == "blocked-by-network":
                out.status = "blocked-by-network"
                break
            continue
        if not j.get("c"):
            errs.append(f"{a['symbol']}: empty quote")
            continue
        out.records.append(quote_record(symbol=a["symbol"], exchange="US", asset_type=a["asset_type"], currency="USD",
                                        provider="finnhub", source_id="finnhub", price=float(j["c"]),
                                        data_ts=ts_from_unix(j.get("t")), extra={"prev_close": j.get("pc")}))
    if errs and out.status == "ok":
        out.status = "partial" if out.records else "bad-response"
    out.error = "; ".join(errs[:8])
    return out


def finnhub_earnings(start, end):
    key = env_key("FINNHUB_API_KEY")
    if not key:
        return ProviderResult("finnhub", "needs-key", [], "set FINNHUB_API_KEY (free)")
    try:
        j = http_json(f"https://finnhub.io/api/v1/calendar/earnings?from={start}&to={end}&token={key}")
    except FetchError as e:
        return _fail("finnhub", e, 1)
    now = iso(utcnow())
    recs = [{"id": new_id("e"), "kind": "event", "event": "earnings", "symbol": e.get("symbol"), "date": e.get("date"),
             "hour": e.get("hour"), "eps_estimate": e.get("epsEstimate"), "observed_at": now, "source_id": "finnhub",
             "claim_type": "estimate", "url": "https://finnhub.io/docs/api/earnings-calendar"}
            for e in j.get("earningsCalendar", [])]
    return ProviderResult("finnhub", "ok", recs, "", 1)


# ---------------------------------------------------------------- FRED
FRED_SERIES = {"CPIAUCSL": "US CPI (index)", "UNRATE": "US unemployment rate", "FEDFUNDS": "Effective fed funds rate",
               "DGS10": "US 10-year Treasury yield", "DCOILWTICO": "WTI crude oil price"}


def fred(series=tuple(FRED_SERIES)):
    key = env_key("FRED_API_KEY")
    if not key:
        return ProviderResult("fred", "needs-key", [], "set FRED_API_KEY (free)")
    out = ProviderResult("fred", "ok")
    for s in series:
        try:
            j = http_json(f"https://api.stlouisfed.org/fred/series/observations?series_id={s}&api_key={key}"
                          "&file_type=json&sort_order=desc&limit=1")
            out.calls += 1
        except FetchError as e:
            return _fail("fred", e, out.calls)
        obs = [o for o in j.get("observations", []) if o.get("value") not in (".", None)]
        if obs:
            out.records.append({"id": new_id("m"), "kind": "macro", "series": s, "label": FRED_SERIES.get(s, s),
                                "value": float(obs[0]["value"]), "data_date": obs[0]["date"],
                                "realtime_start": obs[0].get("realtime_start"), "observed_at": iso(utcnow()),
                                "source_id": "fred", "url": f"https://fred.stlouisfed.org/series/{s}"})
    return out


# ---------------------------------------------------------------- SEC EDGAR (US issuers)
def sec_recent_filings(tickers, forms=("8-K", "10-Q", "10-K")):
    if not env_key("SEC_USER_AGENT"):
        return ProviderResult("sec_edgar", "needs-key", [], "set SEC_USER_AGENT to 'Name contact-email' (SEC requires it)")
    try:
        mapping = http_json("https://www.sec.gov/files/company_tickers.json")
    except FetchError as e:
        return _fail("sec_edgar", e, 1)
    cik = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in mapping.values()}
    out = ProviderResult("sec_edgar", "ok", [], "", 1)
    for t in tickers:
        c = cik.get(t.replace(".", "-").upper())
        if not c:
            continue
        try:
            j = http_json(f"https://data.sec.gov/submissions/CIK{c}.json")
            out.calls += 1
        except FetchError as e:
            out.error = str(e)
            out.status = "partial"
            continue
        r = j.get("filings", {}).get("recent", {})
        for i, form in enumerate(r.get("form", [])[:40]):
            if form in forms:
                acc = r["accessionNumber"][i].replace("-", "")
                out.records.append({"id": new_id("f"), "kind": "filing", "symbol": t, "form": form,
                                    "filed": r["filingDate"][i], "published_at": r.get("acceptanceDateTime", [None] * 40)[i],
                                    "title": f"{t} {form} filed {r['filingDate'][i]}",
                                    "url": f"https://www.sec.gov/Archives/edgar/data/{int(c)}/{acc}/{r['primaryDocument'][i]}",
                                    "observed_at": iso(utcnow()), "source_id": "sec_edgar", "claim_type": "fact",
                                    "origin_id": f"sec:{acc}"})
    return out


# ---------------------------------------------------------------- RSS headlines
def _norm_title(t):
    return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in t).split())


def _parse_date(s):
    if not s:
        return None
    try:
        return iso(parsedate_to_datetime(s))
    except (TypeError, ValueError):
        try:
            return iso(datetime.fromisoformat(s.replace("Z", "+00:00")))
        except ValueError:
            return None


def parse_feed(xml_bytes, source_id):
    root = ET.fromstring(xml_bytes)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = []
    for it in root.iter("item"):
        items.append((it.findtext("title") or "", it.findtext("link") or "", it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date")))
    for e in root.findall("a:entry", ns):
        link = e.find("a:link", ns)
        items.append((e.findtext("a:title", "", ns), link.get("href") if link is not None else "",
                      e.findtext("a:published", None, ns) or e.findtext("a:updated", None, ns)))
    now = iso(utcnow())
    return [{"id": new_id("n"), "kind": "headline", "title": t.strip(), "url": l.strip(), "published_at": _parse_date(d),
             "observed_at": now, "source_id": source_id, "claim_type": "fact", "norm_title": _norm_title(t)}
            for t, l, d in items if t.strip()]


def rss(feeds):
    results = []
    for f in feeds:
        try:
            raw = http_get(f["url"])
            recs = parse_feed(raw, f["source_id"])
            for r in recs:
                r["topic"] = f.get("topic")
            results.append(ProviderResult(f["source_id"], "ok", recs, "", 1))
        except FetchError as e:
            results.append(_fail(f["source_id"], e, 1))
        except ET.ParseError as e:
            results.append(ProviderResult(f["source_id"], "bad-response", [], f"feed XML parse error: {e}", 1))
    return results


def dedupe_headlines(new, existing):
    """Drop headlines already stored, and collapse syndicated copies (same normalized title) into
    the earliest-published one, recording the others as `syndicated_from`. Copies never count as
    independent confirmation."""
    seen_urls = {e.get("url") for e in existing}
    by_title = {}
    for e in existing:
        if e.get("norm_title"):
            by_title.setdefault(e["norm_title"], e)
    out = []
    for r in sorted(new, key=lambda r: r.get("published_at") or "9999"):
        if r["url"] in seen_urls:
            continue
        orig = by_title.get(r["norm_title"])
        if orig:
            r["syndicated_from"] = orig["id"]
            r["origin_id"] = orig.get("origin_id") or orig["id"]
        else:
            r["origin_id"] = r["id"]
            by_title[r["norm_title"]] = r
        seen_urls.add(r["url"])
        out.append(r)
    return out
