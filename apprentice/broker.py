"""Paper broker: the ONLY component that creates fills, and it is simulation-only.

This module deliberately has no network access (no urllib/http/socket imports, enforced by a
test) and no brokerage credentials. Fills use stored real quotes that existed at the time.
"""
from datetime import timedelta

from . import LIVE_TRADING_AVAILABLE, costs, risk, scorecard
from .ledger import Ledger, iso, new_id, parse_ts
from .levels import effective_level
from .market_calendar import ET, CalendarGap, is_open, session
from .portfolio import Portfolio
from .quotebook import QuoteBook
from .validate import age_minutes

assert LIVE_TRADING_AVAILABLE is False

RISK_LIMIT_CHECKS = {"position_size", "risk_per_trade", "sector_limit", "crypto_limit", "daily_loss_halt",
                     "drawdown_review", "max_open_positions", "cash_available", "stop_loss_set", "long_only"}


class PaperBroker:
    def __init__(self, settings, ledger_dir=None):
        self.settings = settings
        self.dir = ledger_dir
        kw = {"directory": ledger_dir} if ledger_dir else {}
        self.L = {n: Ledger(n, **kw) for n in ("orders", "fills", "trades", "valuations", "level_events",
                                                 "research", "quotes", "forecasts", "health")}

    # ------------------------------------------------------------ state
    def portfolio(self):
        return Portfolio.from_fills(self.settings["account"]["starting_balance"], self.L["fills"].read())

    def trades(self):
        out = {}
        for r in self.L["trades"].read():
            t = out.setdefault(r["trade_id"], {"trade_id": r["trade_id"], "events": []})
            t["events"].append(r)
            if r["event"] == "created":
                t.update({k: v for k, v in r.items() if k not in ("event", "seq", "hash", "prev_hash")})
                t["status"] = "pending"
            elif r["event"] == "opened":
                t["status"] = "open"
                t["entry"] = r
            elif r["event"] == "closed":
                t["status"] = "closed"
                t["exit"] = r
            elif r["event"] == "cancelled":
                t["status"] = "cancelled"
                t["cancel"] = r
        return out

    def open_orders(self):
        orders, done = {}, set()
        for r in self.L["orders"].read():
            if r["event"] == "placed":
                orders[r["order_id"]] = r
            else:
                done.add(r["order_id"])
        return [o for oid, o in orders.items() if oid not in done]

    def level(self):
        return effective_level(self.settings, self.L["level_events"].read())

    def _marks(self, book, now, portfolio):
        marks, fx = {}, book.usdcad(now)
        for pos in portfolio.positions.values():
            px, q = book.mark(pos.symbol, now)
            a = self.settings.asset(pos.symbol)
            if px is not None:
                if a["currency"] == "USD":
                    if fx:
                        marks[pos.symbol] = px * fx
                else:
                    marks[pos.symbol] = px
        return marks

    def _known_ids(self):
        ids = set()
        for n in ("research", "quotes", "forecasts"):
            ids |= {r["id"] for r in self.L[n].read() if "id" in r}
        return ids

    def _evidence(self, ids):
        want = set(ids)
        return [r for n in ("research", "quotes", "forecasts") for r in self.L[n].read() if r.get("id") in want]

    # ------------------------------------------------------------ entries
    def propose(self, proposal, now):
        """Check a proposed entry with the risk engine; record it; fill now if possible, else queue."""
        s = self.settings
        book = QuoteBook(self.dir)
        p = dict(proposal)
        p.setdefault("decided_at", iso(now))
        p.setdefault("side", "buy")
        asset = s.asset(p.get("symbol"))
        quote = book.latest(p.get("symbol"), now) if asset else None
        usdcad = book.usdcad(now)
        port = self.portfolio()
        marks = self._marks(book, now, port)
        equity, _ = port.equity(marks)
        est_price = costs.fill_price(s, asset, quote, "buy")["price"] if (asset and quote) else 0.0
        qty, est_cost = 0.0, 0.0
        if asset and quote and est_price > 0:
            fee_pct = s["costs"]["kraken"]["taker_fee_pct"] if asset["asset_type"] == "crypto" else (
                s["costs"]["questrade"]["fx_fee_pct"] if asset["currency"] == "USD" else 0.0)
            if asset["currency"] != "USD" or usdcad:
                qty = p.get("quantity") or risk.size_position(settings=s, asset=asset, est_price=est_price,
                                                               stop=p.get("stop_price"), equity=equity, cash=port.cash,
                                                               usdcad=usdcad, round_qty=costs.round_qty,
                                                               cost_factor=1 + fee_pct)
                qty = costs.round_qty(s, asset, qty)
                if qty > 0:
                    est_cost = -costs.execution(s, asset, quote, "buy", qty, usdcad)["cash_delta_cad"]
        checks = risk.check_entry(settings=s, level=self.level(), proposal=p, asset=asset, quote=quote, usdcad=usdcad,
                                  portfolio=port, marks=marks, valuations=self.L["valuations"].read(),
                                  evidence=self._evidence(p.get("evidence_ids") or []), known_ids=self._known_ids(),
                                  now=now, qty=qty, est_cost_cad=est_cost, est_price=est_price or 1.0)
        failed = [c for c in checks if not c.passed]
        order_id, trade_id = new_id("o"), new_id("t")
        if failed:
            self.L["orders"].append({"event": "rejected_proposal", "order_id": order_id, "symbol": p.get("symbol"),
                                     "strategy": p.get("strategy"), "decided_at": p["decided_at"],
                                     "checks": [c.as_dict() for c in checks],
                                     "reasons": [c.detail for c in failed]}, now=now)
            names = {c.name for c in failed}
            if names & RISK_LIMIT_CHECKS:
                scorecard.award(s, "risk_rule_breach_attempt", "; ".join(c.detail for c in failed if c.name in RISK_LIMIT_CHECKS),
                                order_id, self.dir, now)
            if "evidence_recorded" in names and p.get("evidence_ids"):
                scorecard.award(s, "fabricated_or_unsourced_fact", "cited evidence that is not in the ledger", order_id, self.dir, now)
            if "no_lookahead" in names:
                scorecard.award(s, "timestamp_error", "evidence dated after the decision", order_id, self.dir, now)
            if "price_fresh_enough" in names:
                scorecard.award(s, "used_stale_data", "proposal relied on a stale price", order_id, self.dir, now)
            return {"accepted": False, "order_id": order_id, "checks": [c.as_dict() for c in checks],
                    "reasons": [c.detail for c in failed]}

        strat = s.strategy(p["strategy"])
        self.L["trades"].append({"event": "created", "trade_id": trade_id, "symbol": p["symbol"], "asset_type": asset["asset_type"],
                                 "exchange": asset["exchange"], "currency": asset["currency"], "strategy": p["strategy"],
                                 "experiment": bool(strat.get("experiment")), "decided_at": p["decided_at"],
                                 "evidence_ids": p["evidence_ids"], "decision_quote_id": quote["id"],
                                 "decision_price": quote.get("ask") or quote.get("price"),
                                 "thesis": p["thesis"], "invalidation": p["invalidation"], "exit_rules": p["exit_rules"],
                                 "stop_price": p["stop_price"], "target_price": p["target_price"],
                                 "max_holding_days": p.get("max_holding_days") or strat["holding_days"][1],
                                 "expected_holding": p.get("expected_holding"), "confidence": p.get("confidence"),
                                 "scenarios": p.get("scenarios"), "forecast_id": p.get("forecast_id"),
                                 "planned_qty": qty, "est_cost_cad": est_cost,
                                 "risk_checks": [c.as_dict() for c in checks]}, now=now)
        order = self.L["orders"].append({"event": "placed", "order_id": order_id, "trade_id": trade_id, "symbol": p["symbol"],
                                         "side": "buy", "qty": qty, "type": p.get("order_type", "market"),
                                         "limit_price": p.get("limit_price"), "reason": "entry", "strategy": p["strategy"],
                                         "decided_at": p["decided_at"], "valid_until": iso(self._expiry(asset, now))}, now=now)
        filled = self._try_fill(order, now, book)
        return {"accepted": True, "order_id": order_id, "trade_id": trade_id, "qty": qty, "filled": bool(filled),
                "fill": filled, "checks": [c.as_dict() for c in checks]}

    def _expiry(self, asset, now):
        if asset["asset_type"] == "crypto":
            return now + timedelta(hours=24)
        local = now.astimezone(ET)
        d = local.date()
        for _ in range(10):
            try:
                sess = session(asset["exchange"], d)
            except CalendarGap:
                return now
            if sess and sess[1] > local:
                return sess[1]
            d += timedelta(days=1)
        return now

    def _fill_quote(self, asset, symbol, now, book, strategy):
        q = book.latest(symbol, now)
        if not q:
            return None, "no valid quote"
        if not is_open(asset["exchange"], now):
            return None, "market closed"
        kind = "crypto" if asset["asset_type"] == "crypto" else "stock"
        limit = self.settings.strategy(strategy)["max_fill_quote_age_minutes"][kind] if strategy else 20
        if age_minutes(q, now) > limit:
            return None, f"latest quote is {age_minutes(q, now):.0f} min old (fill limit {limit})"
        dts = parse_ts(q.get("data_ts") or q["observed_at"])
        if asset["asset_type"] != "crypto" and not is_open(asset["exchange"], dts):
            return None, "quote is from outside regular trading hours"
        return q, ""

    def _try_fill(self, order, now, book):
        s = self.settings
        asset = s.asset(order["symbol"])
        q, why = self._fill_quote(asset, order["symbol"], now, book, order.get("strategy"))
        if not q:
            return None
        side = order["side"]
        est = costs.fill_price(s, asset, q, side)["price"]
        if order.get("type") == "limit" and order.get("limit_price") is not None:
            if (side == "buy" and est > order["limit_price"]) or (side == "sell" and est < order["limit_price"]):
                return None
        usdcad = book.usdcad(now)
        if asset["currency"] == "USD" and not usdcad:
            return None
        port = self.portfolio()
        qty = order["qty"]
        if side == "sell":
            pos = port.positions.get(order["trade_id"])
            if not pos:
                return None
            qty = pos.qty
        ex = costs.execution(s, asset, q, side, qty, usdcad)
        if side == "buy" and -ex["cash_delta_cad"] > port.cash + 1e-9:
            self.L["orders"].append({"event": "rejected", "order_id": order["order_id"], "reason": "insufficient cash at fill"}, now=now)
            self.L["trades"].append({"event": "cancelled", "trade_id": order["trade_id"], "reason": "insufficient cash at fill"}, now=now)
            return None
        fill = self.L["fills"].append({"id": new_id("f"), "order_id": order["order_id"], "trade_id": order["trade_id"],
                                       "symbol": order["symbol"], "strategy": order.get("strategy"), "quote_id": q["id"],
                                       "quote_observed_at": q["observed_at"], "quote_data_ts": q.get("data_ts"),
                                       "filled_at": iso(now), "reason": order.get("reason"), **ex}, now=now)
        self.L["orders"].append({"event": "filled", "order_id": order["order_id"], "fill_id": fill["id"]}, now=now)
        if side == "buy":
            self.L["trades"].append({"event": "opened", "trade_id": order["trade_id"], "fill_id": fill["id"], "entry_price": ex["price"],
                                     "qty": qty, "entry_cost_cad": -ex["cash_delta_cad"], "opened_at": iso(now)}, now=now)
        else:
            self._record_close(order, fill, now)
        return fill

    def _record_close(self, order, fill, now):
        port = self.portfolio()
        trades = self.trades()
        t = trades[order["trade_id"]]
        realized = port.realized.get(order["trade_id"], 0.0)
        opened = parse_ts(t["entry"]["opened_at"])
        fees = sum(f["fees_cad"] for f in self.L["fills"].read() if f["trade_id"] == order["trade_id"])
        self.L["trades"].append({"event": "closed", "trade_id": order["trade_id"], "exit_reason": order.get("reason"),
                                 "exit_price": fill["price"], "exit_at": iso(now), "realized_pnl_cad": realized,
                                 "return_pct": realized / t["entry"]["entry_cost_cad"],
                                 "holding_days": (now - opened).total_seconds() / 86400, "fees_cad": fees,
                                 "stop_gap": (order.get("reason") == "stop" and fill["price"] < t["stop_price"])}, now=now)

    # ------------------------------------------------------------ exits & housekeeping
    def request_exit(self, trade_id, reason, now):
        t = self.trades().get(trade_id)
        if not t or t["status"] != "open":
            return None
        if any(o["trade_id"] == trade_id and o["side"] == "sell" for o in self.open_orders()):
            return None
        a = self.settings.asset(t["symbol"])
        return self.L["orders"].append({"event": "placed", "order_id": new_id("o"), "trade_id": trade_id, "symbol": t["symbol"],
                                        "side": "sell", "qty": t["entry"]["qty"], "type": "market", "reason": reason,
                                        "strategy": t["strategy"], "decided_at": iso(now),
                                        "valid_until": iso(now + timedelta(days=30))}, now=now)

    def process(self, now):
        """Run once per scheduled run: fill/expire pending orders, trigger exits, value the portfolio."""
        book = QuoteBook(self.dir)
        notes = []
        for o in self.open_orders():
            if o["side"] == "buy" and parse_ts(o["valid_until"]) <= now:
                self.L["orders"].append({"event": "expired", "order_id": o["order_id"]}, now=now)
                self.L["trades"].append({"event": "cancelled", "trade_id": o["trade_id"], "reason": "entry order expired unfilled"}, now=now)
                notes.append(f"{o['symbol']}: entry order expired unfilled")
                continue
            if self._try_fill(o, now, book):
                notes.append(f"{o['symbol']}: {o['side']} filled ({o['reason']})")
        for t in [t for t in self.trades().values() if t["status"] == "open"]:
            a = self.settings.asset(t["symbol"])
            q = book.latest(t["symbol"], now)
            px = (q.get("bid") if q and q.get("bid") is not None else q.get("price")) if q else None
            reason = None
            if px is not None and px <= t["stop_price"]:
                reason = "stop"
            elif px is not None and px >= t["target_price"]:
                reason = "target"
            elif (now - parse_ts(t["entry"]["opened_at"])).total_seconds() / 86400 >= t["max_holding_days"] and t["max_holding_days"] > 0:
                reason = "time"
            elif t.get("experiment") and a["asset_type"] != "crypto":
                sess = session(a["exchange"], now.astimezone(ET).date())
                force = self.settings.strategy(t["strategy"]).get("force_close_minutes_before_close", 30)
                if sess and now >= sess[1] - timedelta(minutes=force):
                    reason = "end_of_day"
            if reason:
                o = self.request_exit(t["trade_id"], reason, now)
                if o and self._try_fill(o, now, book):
                    notes.append(f"{t['symbol']}: closed ({reason})")
                elif o:
                    notes.append(f"{t['symbol']}: exit ({reason}) queued; no fresh quote or market closed")
            elif px is None:
                notes.append(f"{t['symbol']}: no valid quote, so exits could not be checked (gap risk)")
        return notes + [self.snapshot(now, book)]

    def snapshot(self, now, book=None):
        book = book or QuoteBook(self.dir)
        port = self.portfolio()
        marks = self._marks(book, now, port)
        equity, missing = port.equity(marks)
        ok, lhs, rhs = port.reconcile()
        stale = []
        for pos in port.positions.values():
            px, q = book.mark(pos.symbol, now)
            if q and age_minutes(q, now) > 24 * 60:
                stale.append(pos.symbol)
        v = self.L["valuations"].append({"at": iso(now), "cash": port.cash, "equity": equity,
                                         "positions": [{"trade_id": t, "symbol": p.symbol, "qty": p.qty, "cost_basis_cad": p.cost_basis_cad,
                                                        "mark_cad": marks.get(p.symbol)} for t, p in port.positions.items()],
                                         "unmarked": missing, "stale_marks": stale, "reconciled": ok,
                                         "realized_total": port.realized_total, "fees_cad": port.fees_cad}, now=now)
        if not ok:
            self.L["health"].append({"level": "error", "what": "reconciliation", "detail": f"cash+basis {lhs:.6f} != start+realized {rhs:.6f}"}, now=now)
        self._maybe_demote(equity, now)
        return f"valued at ${equity:.2f} (cash ${port.cash:.2f}){'; reconciliation FAILED' if not ok else ''}"

    def _maybe_demote(self, equity, now):
        from .settings import config_hash
        vals = self.L["valuations"].read()
        peak = max([v["equity"] for v in vals] + [self.settings["account"]["starting_balance"]])
        dd = equity / peak - 1
        lvl = self.level()
        if lvl >= 2 and dd <= -self.settings["promotion"]["demotion"]["drawdown_pct"]:
            h = config_hash(self.settings.config_dir)
            if not any(e.get("reason_code") == "drawdown" and e.get("config_hash") == h for e in self.L["level_events"].read()):
                self.L["level_events"].append({"event": "demotion", "from_level": lvl, "to_level": lvl - 1, "reason_code": "drawdown",
                                               "reason": f"Drawdown {dd:.1%} from peak breached the {self.settings['promotion']['demotion']['drawdown_pct']:.0%} limit.",
                                               "config_hash": h}, now=now)
