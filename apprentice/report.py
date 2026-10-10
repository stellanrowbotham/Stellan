"""Builds the research report from the agent's structured input. Code checks that every required
field is present, scores and ranks the candidates, and writes plain-language Markdown and HTML.
If nothing passes, the report says NO_TRADE. A report is a set of hypotheses, not a promise."""
import html
from pathlib import Path

from . import costs, risk
from .ledger import Ledger, iso, new_id, parse_ts
from .levels import NAMES
from .market_calendar import ET
from .quotebook import QuoteBook
from .scoring import NO_TRADE, score

REPORT_DIR = Path(__file__).resolve().parent / "reports"
REQUIRED = {
    "symbol": "ticker", "name": "asset name", "why_considered": "why it's being considered",
    "news": "important news and developments", "technicals": "technical indicators and price levels",
    "catalysts": "upcoming catalysts/events", "bull_case": "bullish arguments", "bear_case": "bearish arguments",
    "risks": "main risks", "invalidation": "what would prove the idea wrong", "entry_conditions": "entry price/conditions",
    "exit_conditions": "exit and profit-taking rules", "stop_plan": "stop-loss/risk plan", "holding_period": "intended holding period",
    "scenarios": "upside and downside scenarios", "confidence": "confidence level", "confidence_basis": "measurable evidence for the confidence",
    "quote_id": "price record used", "evidence_ids": "evidence records", "entry_price": "planned entry price",
    "stop_price": "stop price", "target_price": "target price", "strategy": "strategy",
}
PLAIN = {
    "stop": "Stop-loss: a price where we sell automatically to stop a loss from getting bigger.",
    "target": "Target: the price where we plan to take the profit.",
    "rr": "Reward-to-risk: how much we could win for each $1 we could lose. 2 means win $2 for every $1 risked.",
    "rsi": "RSI: a 0-100 score of how fast the price has been rising. Over 70 can mean 'ran up too fast'; under 30 'fell too fast'.",
    "sma": "Moving average: the average price over the last N days. It shows the trend.",
    "brier": "Brier score: how good the predictions are. 0 is perfect, and 0.25 is what guessing 50/50 would get.",
}


def _missing(c):
    out = []
    for k, label in REQUIRED.items():
        v = c.get(k)
        if v in (None, "", [], {}):
            out.append(label)
    sc = c.get("scenarios") or {}
    if isinstance(sc, dict) and not ({"upside", "downside"} <= set(sc)):
        out.append("both upside and downside scenarios")
    return out


def build(settings, broker, payload, now, run_name):
    kw = {"directory": broker.dir} if broker.dir else {}
    book = QuoteBook(broker.dir)
    pool = {r["id"]: r for n in ("research", "quotes", "forecasts") for r in Ledger(n, **kw).read() if "id" in r}
    level = broker.level()
    port = broker.portfolio()
    marks = broker._marks(book, now, port)
    equity, _ = port.equity(marks)
    usdcad = book.usdcad(now)
    rows = []
    for c in payload.get("candidates", []):
        miss = _missing(c)
        q = pool.get(c.get("quote_id"))
        ev = [pool[i] for i in c.get("evidence_ids", []) if i in pool]
        bad_ids = [i for i in c.get("evidence_ids", []) if i not in pool]
        if q is None:
            miss.append("a price record that exists in the ledger")
        s = score(settings, {**c, "asset_type": (settings.asset(c.get("symbol")) or {}).get("asset_type")}, ev, q, now)
        a = settings.asset(c.get("symbol"))
        size = None
        if a and q and c.get("stop_price") and c.get("entry_price"):
            fee = settings["costs"]["kraken"]["taker_fee_pct"] if a["asset_type"] == "crypto" else (
                settings["costs"]["questrade"]["fx_fee_pct"] if a["currency"] == "USD" else 0.0)
            if a["currency"] != "USD" or usdcad:
                est = costs.fill_price(settings, a, q, "buy")["price"]
                qty = risk.size_position(settings=settings, asset=a, est_price=est, stop=c["stop_price"], equity=equity,
                                         cash=port.cash, usdcad=usdcad, round_qty=costs.round_qty, cost_factor=1 + fee)
                if qty > 0:
                    size = {"qty": qty, "cost_cad": round(-costs.execution(settings, a, q, "buy", qty, usdcad)["cash_delta_cad"], 2)}
                else:
                    size = {"qty": 0, "note": "Too expensive for the position limit (whole shares only)."}
        rows.append({"c": c, "score": s, "missing": miss, "bad_ids": bad_ids, "quote": q, "evidence": ev, "size": size,
                     "tradeable": s["tradeable"] and not miss and not bad_ids})
    rows.sort(key=lambda r: (r["tradeable"], r["score"]["total"]), reverse=True)
    passing = [r for r in rows if r["tradeable"]]
    rid = new_id("rep")
    stamp = now.astimezone(ET).strftime("%Y-%m-%d-%H%M")
    md = _markdown(settings, payload, rows, passing, level, equity, port, now, run_name)
    REPORT_DIR.mkdir(exist_ok=True)
    md_path = REPORT_DIR / f"{stamp}-{run_name}.md"
    html_path = REPORT_DIR / f"{stamp}-{run_name}.html"
    md_path.write_text(md)
    html_path.write_text(_html(md))
    rec = Ledger("reports", **kw).append({
        "id": rid, "run": run_name, "at": iso(now), "level": level, "no_trade": not passing,
        "headline": NO_TRADE if not passing else f"{len(passing)} candidate(s) meet the criteria",
        "market_summary": payload.get("market_summary", {}), "sources_searched": payload.get("sources_searched", []),
        "limitations": payload.get("limitations", []),
        "candidates": [{"symbol": r["c"].get("symbol"), "name": r["c"].get("name"), "score": r["score"], "tradeable": r["tradeable"],
                        "missing": r["missing"], "bad_ids": r["bad_ids"], "size": r["size"],
                        "price": (r["quote"] or {}).get("price") or (r["quote"] or {}).get("ask"),
                        "price_ts": (r["quote"] or {}).get("data_ts") or (r["quote"] or {}).get("observed_at"),
                        "sources": [{"title": e.get("title") or e.get("label") or e.get("symbol"), "url": e.get("url"),
                                     "published_at": e.get("published_at") or e.get("data_date") or e.get("data_ts"),
                                     "source_id": e.get("source_id")} for e in r["evidence"]],
                        **{k: r["c"].get(k) for k in REQUIRED if k not in ("evidence_ids",)}} for r in rows],
        "md_path": str(md_path.relative_to(REPORT_DIR.parent.parent)),
    }, now=now)
    return rec, md_path, html_path


def _fmt_ts(s):
    if not s:
        return "unknown time"
    return parse_ts(s).astimezone(ET).strftime("%a %b %d, %I:%M %p ET")


def _markdown(settings, payload, rows, passing, level, equity, port, now, run_name):
    o = []
    title = {"pre_market": "Morning research report", "post_close": "After-the-bell update", "crypto": "Crypto check",
             "day_experiment": "Hourly experiment check"}.get(run_name, "Research report")
    o.append(f"# {title}: {now.astimezone(ET).strftime('%A %B %d, %Y, %I:%M %p ET')}")
    o.append(f"**Level {level}: {NAMES[level]}** · Pretend account: **${equity:,.2f} CAD** (started at ${settings['account']['starting_balance']:,.0f}) · Cash ${port.cash:,.2f}")
    o.append("> This is practice with pretend money. Every idea below is a *guess with reasons*, not a promise. A high score does not mean a trade will work.")
    if level < 2:
        o.append("> 🎓 **Level 1 means forecasts only.** The apprentice is still proving its research is honest and accurate, so no pretend trades are placed yet.")
    ms = payload.get("market_summary") or {}
    if ms.get("text"):
        o.append("## What's happening in the markets (in plain words)\n" + ms["text"])
    o.append("## Bottom line")
    if passing:
        o.append(f"**{len(passing)} idea(s) pass every check.** Best: **{passing[0]['c']['symbol']}** (score {passing[0]['score']['total']:.0f}/100).")
    else:
        o.append(f"**{NO_TRADE}**")
    for i, r in enumerate(rows, 1):
        c, s, q = r["c"], r["score"], r["quote"]
        o.append(f"## {i}. {c.get('name', '?')} ({c.get('symbol')}) · {'✅ passes' if r['tradeable'] else '❌ does not pass'} · score {s['total']:.0f}/100")
        if q:
            px = q.get("price") if q.get("price") is not None else q.get("ask")
            o.append(f"**Latest price:** {px:,.4f} {settings.asset(c['symbol'])['currency']} ({'bid/ask quoted' if q.get('bid') is not None else 'last price'}), "
                     f"data time {_fmt_ts(q.get('data_ts') or q.get('observed_at'))}, from {q['provider']}.")
        if r["missing"]:
            o.append("⚠️ **Missing (so it can't pass):** " + ", ".join(r["missing"]))
        if r["bad_ids"]:
            o.append("⚠️ **Cited records that don't exist:** " + ", ".join(r["bad_ids"]))
        for label, key in (("Why we're looking at it", "why_considered"), ("News", "news"), ("Chart clues (technicals)", "technicals"),
                           ("Coming up (catalysts)", "catalysts"), ("Why it might go up 🐂", "bull_case"),
                           ("Why it might go down 🐻", "bear_case"), ("Main risks", "risks"), ("We're wrong if…", "invalidation"),
                           ("When to buy", "entry_conditions"), ("When to sell", "exit_conditions"), ("Safety plan (stop-loss)", "stop_plan"),
                           ("How long to hold", "holding_period")):
            v = c.get(key)
            if v:
                if isinstance(v, list):
                    v = "\n" + "\n".join(f"- {x}" for x in v)
                elif isinstance(v, dict):
                    v = "\n" + "\n".join(f"- {k}: {x}" for k, x in v.items())
                o.append(f"**{label}:** {v}")
        sc = c.get("scenarios") or {}
        if sc:
            o.append(f"**If it goes well:** {sc.get('upside')} · **If it goes badly:** {sc.get('downside')}")
        if c.get("entry_price") and c.get("stop_price") and c.get("target_price"):
            o.append(f"**Plan:** buy near {c['entry_price']}, sell at {c['target_price']} for profit, or at {c['stop_price']} to stop the loss. "
                     f"Reward-to-risk {s['reward_risk']:.1f}. ({PLAIN['rr']})")
        if r["size"]:
            o.append(f"**Suggested pretend size:** {r['size'].get('qty')} units"
                     + (f" ≈ ${r['size']['cost_cad']:.2f} CAD including fees" if r['size'].get('cost_cad') else f" ({r['size'].get('note')})"))
        o.append(f"**Confidence:** {c.get('confidence')}. Why: {c.get('confidence_basis')}")
        o.append("**Score breakdown:** " + ", ".join(f"{k} {v:.2f}" for k, v in s["parts"].items())
                 + " · Checks: " + "; ".join(f"{'✓' if g['passed'] else '✗'} {g['detail']}" for g in s["gates"].values()))
        if r["evidence"]:
            o.append("**Sources:**\n" + "\n".join(
                f"- [{e.get('title') or e.get('label') or e.get('symbol')}]({e.get('url') or ''}) · "
                f"{e.get('source_id') or e.get('provider')} · published {_fmt_ts(e.get('published_at') or e.get('data_ts') or e.get('observed_at'))}"
                + (" · copy of another story" if e.get("syndicated_from") else "")
                + (f" · {e.get('claim_type')}" if e.get("claim_type") and e.get("claim_type") != "fact" else "")
                for e in r["evidence"]))
    if payload.get("sources_searched"):
        o.append("## What I actually checked\n" + "\n".join(f"- {x}" for x in payload["sources_searched"]))
    if payload.get("limitations"):
        o.append("## Limits of this report\n" + "\n".join(f"- {x}" for x in payload["limitations"]))
    o.append("## Words to know\n" + "\n".join(f"- {v}" for v in PLAIN.values()))
    return "\n\n".join(o) + "\n"


def _html(md):
    """Tiny Markdown-to-HTML for email (headings, bold, lists, links, quotes)."""
    import re
    out, in_list = [], False
    for line in md.splitlines():
        esc = html.escape(line)
        esc = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc)
        esc = re.sub(r"\*(.+?)\*", r"<i>\1</i>", esc)
        esc = re.sub(r"\[(.+?)\]\((.*?)\)", r'<a href="\2">\1</a>', esc)
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{esc[2:]}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if line.startswith("## "):
            out.append(f"<h2>{esc[3:]}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{esc[2:]}</h1>")
        elif line.startswith("&gt; "):
            out.append(f"<blockquote>{esc[5:]}</blockquote>")
        elif line.strip():
            out.append(f"<p>{esc}</p>")
    if in_list:
        out.append("</ul>")
    return ("<html><body style=\"font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:680px;margin:auto;line-height:1.5\">"
            + "\n".join(out) + "</body></html>")
