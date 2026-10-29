"""Rules-first trade ideas: the lab's *passing* rules decide what to hold; the AI only reads the news
and may veto. Each signal is written to the research ledger (so proposals can cite it) with its
evidence grade, entry, ATR-based stop and target.

Since 2026-10-29 (Stellan: "if it keeps on rising keep it till it looks like it is going to drop"), momentum
rules use a TRAILING stop 3x ATR below the price that follows winners up, and a far target (10x ATR) that is
only a backstop; the rule's own exit (falls out of the ranking or below its average) does the selling.
Short-term rules (rsi2) keep the fixed 2x ATR stop and 3.1x ATR target."""
from . import history, indicators, lab
from .ledger import Ledger, iso, new_id, utcnow

STOP_ATR, TARGET_ATR = 2.0, 3.1  # short-term rules: reward:risk 1.55, just above the 1.5 gate
RUN_STOP_ATR, RUN_TARGET_ATR = 3.0, 10.0  # momentum rules: trailing stop, far backstop target
LET_RUN = {"momentum", "momentum_buffer"}


def grade(folds):
    return "strong" if folds >= 5 else "weak" if folds >= 2 else "none"


def compute(settings, broker, now=None, write=True):
    now = now or utcnow()
    res = lab.latest()
    if not res:
        return {"error": "no lab results yet: run `python3 -m apprentice lab`"}
    held = {t["symbol"]: t for t in broker.trades().values() if t["status"] in ("open", "pending")}
    port = broker.portfolio()
    equity = port.cash + sum(p.cost_basis_cad for p in port.positions.values())
    max_pos = settings.risk["max_position_pct"] * equity
    whole = not settings["costs"]["questrade"]["fractional_shares"].get("US", False)
    buys, exits, skipped = [], [], []
    led = Ledger("research", **({"directory": broker.dir} if broker.dir else {}))
    for gname, g in res["groups"].items():
        if "error" in g:
            continue
        dates, closes = lab.panel(g["symbols"])
        if not closes:
            continue
        for rule in g["passing"]:
            r = g["rules"][rule]
            w = lab.current(rule, r["live_params"], closes)
            want = {s for s, x in w.items() if x > 0}
            for s in sorted(want):
                a = settings.asset(s)
                if not a:
                    skipped.append({"symbol": s, "why": "research-only proxy, not in the approved list"})
                    continue
                if s in held:
                    continue
                bars = history.load(s)["bars"]
                atr = indicators.atr([b["high"] for b in bars], [b["low"] for b in bars], [b["close"] for b in bars])
                px = bars[-1]["close"]
                if not atr:
                    skipped.append({"symbol": s, "why": "not enough history for ATR"})
                    continue
                if a["asset_type"] != "crypto" and whole and px * (1.0 if a["currency"] == "CAD" else 1.4) > max_pos:
                    skipped.append({"symbol": s, "why": f"one share (~{px:.0f} {a['currency']}) is over the {settings.risk['max_position_pct']:.0%} position cap"})
                    continue
                runs = rule in LET_RUN
                stop_k, target_k = (RUN_STOP_ATR, RUN_TARGET_ATR) if runs else (STOP_ATR, TARGET_ATR)
                sig = {"id": new_id("sg"), "kind": "signal", "title": f"{rule} rule says hold {s} ({gname})",
                       "symbol": s, "rule": f"{gname}/{rule}", "params": r["live_params"], "claim_type": "estimate",
                       "source_id": "strategy_lab", "evidence_grade": grade(r["folds"]), "test_folds": r["folds"],
                       "oos": r["oos"], "buy_hold_oos": r["buy_hold_oos"], "history_last_date": bars[-1]["date"],
                       "history_source": history.load(s)["source"], "last_close": px, "atr14": atr,
                       "entry_price": px, "stop_price": round(px - stop_k * atr, 6), "target_price": round(px + target_k * atr, 6),
                       "trail_distance": round(stop_k * atr, 6) if runs else None,
                       "observed_at": iso(now), "published_at": iso(now)}
                if write:
                    led.append(sig, now=now)
                buys.append(sig)
            for s, t in held.items():
                if t.get("rule") == f"{gname}/{rule}" and s not in want:
                    exits.append({"trade_id": t["trade_id"], "symbol": s, "rule": t["rule"], "why": "rule no longer holds it"})
    return {"buys": buys, "exits": exits, "skipped": skipped, "lab_run_at": res["run_at"]}
