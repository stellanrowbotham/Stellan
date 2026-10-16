"""Order slips for mirroring the apprentice's trades by hand in another simulator (Investopedia).

Investopedia has no official API, so nothing is placed automatically. Each fill becomes a plain
instruction Stellan types in himself. A slip is marked sent only after the email goes out, so none is
lost or sent twice."""
import html

from .ledger import Ledger, new_id
from .market_calendar import ET
from .ledger import parse_ts


def _ticker(asset):
    if asset["asset_type"] == "crypto":
        return asset["symbol"].replace("CAD", "").replace("XBT", "BTC"), "crypto (check that your Investopedia game lists it)"
    if asset["exchange"] == "TSX":
        return asset["symbol"], "Toronto (TSX) stock (only if your game includes the Canadian market; it may be listed as " + asset["symbol"] + ".TO)"
    return asset["symbol"], "US stock"


def pending(settings, broker):
    kw = {"directory": broker.dir} if broker.dir else {}
    sent = {s["fill_id"] for s in Ledger("slips", **kw).read()}
    trades = broker.trades()
    out = []
    for f in Ledger("fills", **kw).read():
        if f["id"] in sent:
            continue
        a = settings.asset(f["symbol"])
        t = trades.get(f["trade_id"], {})
        tick, where = _ticker(a)
        when = parse_ts(f["filled_at"]).astimezone(ET).strftime("%a %b %d, %I:%M %p ET")
        if f["side"] == "buy":
            if a["asset_type"] == "crypto":
                qty_txt = f"about ${f['notional_cad']:.2f} CAD worth ({f['qty']:.6f} {tick})"
            else:
                qty_txt = f"{int(f['qty'])} shares"
            lines = [f"BUY {qty_txt} of {tick}: market order.",
                     f"Then add a STOP (sell) order at {t.get('stop_price')}, the safety exit if it drops.",
                     f"And a LIMIT (sell) order at {t.get('target_price')}, which takes the profit."]
        else:
            lines = [f"SELL ALL your {tick}: market order.",
                     "Cancel the stop and limit orders you set for it.",
                     f"Reason: {f.get('reason')}."]
        out.append({"fill_id": f["id"], "symbol": tick, "where": where, "when": when, "side": f["side"],
                    "apprentice_price": round(f["price"], 6), "lines": lines})
    return out


def render(slips):
    subject = f"Investopedia order slip: {len(slips)} trade(s) to copy"
    text = ["Copy these into your Investopedia simulator. Prices there may differ a little from the apprentice's.", ""]
    rows = []
    for s in slips:
        text += [f"{s['side'].upper()} {s['symbol']} ({s['where']}) · apprentice filled {s['when']} at {s['apprentice_price']}"] + \
                [f"  - {l}" for l in s["lines"]] + [""]
        rows.append(f"<h3>{html.escape(s['side'].upper())} {html.escape(s['symbol'])}</h3><p style='color:#5b6878'>"
                    f"{html.escape(s['where'])} · apprentice filled {html.escape(s['when'])} at {s['apprentice_price']}</p><ol>"
                    + "".join(f"<li>{html.escape(l)}</li>" for l in s["lines"]) + "</ol>")
    body_html = ("<div style='font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:620px'>"
                 "<p>Copy these into your Investopedia simulator. Prices there may differ a little from the apprentice's.</p>"
                 + "".join(rows) + "</div>")
    return subject, "\n".join(text), body_html


def mark_sent(broker, slips, now):
    kw = {"directory": broker.dir} if broker.dir else {}
    led = Ledger("slips", **kw)
    for s in slips:
        led.append({"id": new_id("sl"), "fill_id": s["fill_id"], "symbol": s["symbol"], "side": s["side"]}, now=now)
