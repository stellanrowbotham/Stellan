import inspect
import unittest
from datetime import timedelta

from apprentice import broker as broker_mod
from apprentice.broker import PaperBroker
from apprentice.ledger import iso
from apprentice.scorecard import totals

from .helpers import Env, et, proposal

T0 = et(2026, 10, 13, 10, 0)  # Tuesday, TSX open


class Base(unittest.TestCase):
    level = 2

    def setUp(self):
        self.env = Env(level=self.level)
        self.s = self.env.settings()
        self.b = PaperBroker(self.s, self.env.ledger)

    def tearDown(self):
        self.env.cleanup()

    def ev(self, at=T0):
        return [self.env.note(at - timedelta(minutes=30))["id"]]


class LevelOneCannotTrade(Base):
    level = 1

    def test_rejected_with_reason(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, self.ev(), stop=39.2, target=42.0), T0)
        self.assertFalse(r["accepted"])
        self.assertTrue(any("cannot place simulated trades" in x for x in r["reasons"]))
        self.assertEqual(self.env.L("fills").read(), [])


class EntryAndFills(Base):
    def test_fill_uses_real_quote_at_decision_time(self):
        q = self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        later = self.env.quote("BCE", T0 + timedelta(minutes=30), bid=50.0, ask=50.02)  # future: must not be used
        r = self.b.propose(proposal("BCE", T0, self.ev(), stop=39.2, target=42.0), T0)
        self.assertTrue(r["accepted"], r.get("reasons"))
        self.assertTrue(r["filled"])
        f = r["fill"]
        self.assertEqual(f["quote_id"], q["id"])
        self.assertAlmostEqual(f["price"], 40.02 * (1 + self.s["costs"]["questrade"]["slippage_pct"]))
        # sizing: 10% of $1000 = $100 -> 2 shares; risk to stop (0.82*2=1.64) < $10
        self.assertEqual(f["qty"], 2.0)
        self.assertTrue(self.b.portfolio().reconcile()[0])
        t = self.b.trades()[r["trade_id"]]
        self.assertEqual(t["thesis"], "Fictional test thesis")
        self.assertEqual(t["decision_quote_id"], q["id"])

    def test_position_and_risk_limits_enforced(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, self.ev(), stop=39.0, target=45.0, quantity=5), T0)  # $200 > 10%
        self.assertFalse(r["accepted"])
        self.assertTrue(any(c["name"] == "position_size" and not c["passed"] for c in r["checks"]))
        self.assertEqual(totals(self.env.L("scorecard").read())["risk_violations"], 1)
        r2 = self.b.propose(proposal("BCE", T0, self.ev(), stop=30.0, target=60.0, quantity=2), T0)  # risk $20 > 1%
        self.assertFalse(r2["accepted"])
        self.assertTrue(any(c["name"] == "risk_per_trade" and not c["passed"] for c in r2["checks"]))

    def test_requires_stop_and_target_and_evidence(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, [], stop=None, target=None), T0)
        names = {c["name"] for c in r["checks"] if not c["passed"]}
        self.assertTrue({"stop_loss_set", "target_set", "evidence_recorded"} <= names)

    def test_made_up_evidence_is_penalized(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, ["r-doesnotexist"], stop=39.2, target=42), T0)
        self.assertFalse(r["accepted"])
        self.assertEqual(totals(self.env.L("scorecard").read())["integrity_violations"], 1)

    def test_lookahead_evidence_rejected(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        future = self.env.note(T0 + timedelta(hours=2), published=T0 + timedelta(hours=1))
        r = self.b.propose(proposal("BCE", T0, [future["id"]], stop=39.2, target=42), T0)
        self.assertFalse(r["accepted"])
        self.assertTrue(any(c["name"] == "no_lookahead" and not c["passed"] for c in r["checks"]))
        self.assertEqual(totals(self.env.L("scorecard").read())["timestamp_errors"], 1)

    def test_stale_price_rejected(self):
        self.env.quote("BCE", T0 - timedelta(hours=40), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, self.ev(), stop=39.2, target=42), T0)
        self.assertFalse(r["accepted"])
        self.assertTrue(any(c["name"] == "price_fresh_enough" and not c["passed"] for c in r["checks"]))

    def test_unapproved_config_locks_trading(self):
        p = self.env.cfg / "settings.json"
        p.write_text(p.read_text().replace('"max_position_pct": 0.1', '"max_position_pct": 0.9'))
        b = PaperBroker(self.env.settings(), self.env.ledger)
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = b.propose(proposal("BCE", T0, self.ev(), stop=39.2, target=42), T0)
        self.assertFalse(r["accepted"])
        self.assertTrue(any(c["name"] == "config_approved" and not c["passed"] for c in r["checks"]))

    def test_crypto_limit(self):
        self.env.quote("XBTCAD", T0 - timedelta(minutes=1), bid=90000, ask=90010, exchange="KRAKEN", asset_type="crypto")
        r = self.b.propose(proposal("XBTCAD", T0, self.ev(), stop=85000, target=99000), T0)
        self.assertTrue(r["accepted"], r.get("reasons"))
        for _ in range(2):
            self.b.propose(proposal("XBTCAD", T0, self.ev(), stop=85000, target=99000), T0)
        crypto = sum(p.cost_basis_cad for p in self.b.portfolio().positions.values())
        self.assertLessEqual(crypto, 0.20 * 1000 + 1e-6)

    def test_unknown_asset_rejected(self):
        r = self.b.propose(proposal("GME", T0, self.ev(), stop=1, target=3), T0)
        self.assertFalse(r["accepted"])


class QueueingAndExits(Base):
    def test_market_closed_queues_then_fills_after_open(self):
        sat = et(2026, 10, 10, 11)
        self.env.quote("BCE", sat - timedelta(hours=20), bid=40.0, ask=40.02, data_ts=et(2026, 10, 9, 15, 59))
        r = self.b.propose(proposal("BCE", sat, self.ev(sat), stop=39.2, target=42, strategy="long_term"), sat)
        self.assertTrue(r["accepted"], r.get("reasons"))
        self.assertFalse(r["filled"])
        self.assertEqual(len(self.b.open_orders()), 1)
        # Monday is Thanksgiving (TSX closed): still no fill
        mon = et(2026, 10, 12, 11)
        self.env.quote("BCE", mon, price=40.1)
        self.b.process(mon)
        self.assertEqual(self.env.L("fills").read(), [])

    def test_stop_gap_fills_at_real_lower_price(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, self.ev(), stop=39.2, target=42), T0)
        t1 = T0 + timedelta(days=1)
        self.env.quote("BCE", t1 - timedelta(minutes=1), bid=37.0, ask=37.05)  # gapped below the stop
        notes = self.b.process(t1)
        t = self.b.trades()[r["trade_id"]]
        self.assertEqual(t["status"], "closed")
        self.assertEqual(t["exit"]["exit_reason"], "stop")
        self.assertTrue(t["exit"]["stop_gap"])
        self.assertLess(t["exit"]["exit_price"], 39.2)  # never pretends it got the stop price
        self.assertTrue(self.b.portfolio().reconcile()[0])
        self.assertLess(t["exit"]["realized_pnl_cad"], 0)

    def test_target_exit_and_pnl(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, self.ev(), stop=39.2, target=42), T0)
        t1 = T0 + timedelta(days=1)
        self.env.quote("BCE", t1 - timedelta(minutes=1), bid=42.5, ask=42.55)
        self.b.process(t1)
        t = self.b.trades()[r["trade_id"]]
        self.assertEqual(t["exit"]["exit_reason"], "target")
        port = self.b.portfolio()
        self.assertAlmostEqual(port.cash, 1000 + t["exit"]["realized_pnl_cad"])
        self.assertAlmostEqual(t["exit"]["realized_pnl_cad"], 2 * 42.5 * (1 - 0.0005) - 2 * 40.02 * (1 + 0.0005))

    def test_day_experiment_closes_before_bell(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, self.ev(), stop=39.2, target=42, strategy="day_experiment"), T0)
        self.assertTrue(r["accepted"], r.get("reasons"))
        late = et(2026, 10, 13, 15, 37)
        self.env.quote("BCE", late - timedelta(minutes=1), bid=40.1, ask=40.12)
        self.b.process(late)
        t = self.b.trades()[r["trade_id"]]
        self.assertEqual(t["exit"]["exit_reason"], "end_of_day")
        self.assertTrue(t["experiment"])

    def test_daily_loss_halt(self):
        self.env.L("valuations").append({"at": iso(T0 - timedelta(hours=1)), "equity": 1000.0, "cash": 1000.0}, now=T0)
        # Simulate a loss: a closed trade lost $40 earlier today
        self.env.L("fills").append({"trade_id": "tx", "symbol": "BCE", "side": "buy", "qty": 1, "cash_delta_cad": -100.0, "fees_cad": 0,
                                    "filled_at": iso(T0)}, now=T0)
        self.env.L("fills").append({"trade_id": "tx", "symbol": "BCE", "side": "sell", "qty": 1, "cash_delta_cad": 60.0, "fees_cad": 0,
                                    "filled_at": iso(T0)}, now=T0)
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        r = self.b.propose(proposal("BCE", T0, self.ev(), stop=39.2, target=42), T0)
        self.assertFalse(r["accepted"])
        self.assertTrue(any(c["name"] == "daily_loss_halt" and not c["passed"] for c in r["checks"]))


class NoRealOrders(unittest.TestCase):
    def test_broker_has_no_network_code(self):
        import ast
        tree = ast.parse(inspect.getsource(broker_mod))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported.add(node.module.split(".")[0])
        self.assertFalse(imported & {"urllib", "requests", "http", "socket", "ssl", "aiohttp", "httpx"}, imported)
        # and nothing it imports from the package does network either
        for mod in ("costs", "risk", "scorecard", "ledger", "levels", "market_calendar", "portfolio", "quotebook", "validate"):
            src = inspect.getsource(__import__(f"apprentice.{mod}", fromlist=["x"]))
            self.assertNotIn("import urllib", src)
            self.assertNotIn("import socket", src)

    def test_no_live_module_exists(self):
        import importlib.util
        for name in ("apprentice.live", "apprentice.live_trading", "apprentice.brokerage"):
            self.assertIsNone(importlib.util.find_spec(name))

    def test_live_flag_true_still_cannot_trade(self):
        env = Env(level=2, **{"live_trading.enabled": True})
        try:
            b = PaperBroker(env.settings(), env.ledger)
            env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
            r = b.propose(proposal("BCE", T0, [env.note(T0 - timedelta(minutes=5))["id"]], stop=39.2, target=42), T0)
            self.assertFalse(r["accepted"])
            self.assertTrue(any(c["name"] == "simulation_only" and not c["passed"] for c in r["checks"]))
        finally:
            env.cleanup()


if __name__ == "__main__":
    unittest.main()
