import json
import unittest
from datetime import date, timedelta

import apprentice
from apprentice import costs, indicators, market_calendar as mc
from apprentice.ledger import Ledger, iso
from apprentice.portfolio import Portfolio
from apprentice.settings import CONFIG_DIR, Settings, is_approved

from .helpers import Env, et


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.cleanup()

    def test_chain_verifies_and_detects_edits(self):
        L = self.env.L("forecasts")
        for i in range(3):
            L.append({"id": f"x{i}", "probability": 0.6})
        self.assertEqual(L.verify(), [])
        lines = L.path.read_text().splitlines()
        rec = json.loads(lines[1])
        rec["probability"] = 0.9  # rewrite an old prediction after the fact
        lines[1] = json.dumps(rec, sort_keys=True)
        L.path.write_text("\n".join(lines) + "\n")
        self.assertTrue(any("changed" in p for p in L.verify()))

    def test_detects_deleted_line(self):
        L = self.env.L("trades")
        for i in range(3):
            L.append({"trade_id": f"t{i}", "event": "created"})
        lines = L.path.read_text().splitlines()
        L.path.write_text("\n".join([lines[0], lines[2]]) + "\n")
        self.assertTrue(L.verify())

    def test_caller_cannot_set_hash(self):
        with self.assertRaises(ValueError):
            self.env.L("x").append({"hash": "abc"})


class ConfigTests(unittest.TestCase):
    def test_repo_config_is_approved(self):
        self.assertTrue(is_approved(CONFIG_DIR), "settings.json/universe.json differ from approved.sha256")

    def test_live_trading_absent(self):
        self.assertFalse(apprentice.LIVE_TRADING_AVAILABLE)
        self.assertFalse(Settings()["live_trading"]["enabled"])

    def test_edit_without_approval_is_detected(self):
        env = Env()
        try:
            p = env.cfg / "settings.json"
            s = json.loads(p.read_text())
            s["risk"]["max_position_pct"] = 0.9  # the agent loosening its own limit
            p.write_text(json.dumps(s))
            self.assertFalse(env.settings().approved)
        finally:
            env.cleanup()


class CalendarTests(unittest.TestCase):
    def test_holidays_and_hours(self):
        self.assertFalse(mc.is_open("TSX", et(2026, 10, 12, 11)))  # Canadian Thanksgiving
        self.assertTrue(mc.is_open("US", et(2026, 10, 12, 11)))
        self.assertFalse(mc.is_open("TSX", et(2026, 10, 13, 9, 29)))
        self.assertTrue(mc.is_open("TSX", et(2026, 10, 13, 9, 30)))
        self.assertFalse(mc.is_open("TSX", et(2026, 10, 13, 16, 0)))
        self.assertFalse(mc.is_open("US", et(2026, 7, 3, 11)))  # July 4 observed
        self.assertFalse(mc.is_open("TSX", et(2026, 10, 10, 11)))  # Saturday
        self.assertTrue(mc.is_open("KRAKEN", et(2026, 10, 10, 3)))

    def test_early_close(self):
        self.assertTrue(mc.is_open("US", et(2026, 11, 27, 12, 59)))
        self.assertFalse(mc.is_open("US", et(2026, 11, 27, 13, 0)))

    def test_uncovered_year_fails_safe(self):
        self.assertFalse(mc.is_open("TSX", et(2029, 3, 6, 11)))
        with self.assertRaises(mc.CalendarGap):
            mc.is_trading_day("TSX", date(2029, 3, 6))

    def test_trading_days_between(self):
        self.assertEqual(mc.trading_days_between("TSX", date(2026, 10, 12), date(2026, 10, 16)), 4)


class CostTests(unittest.TestCase):
    def setUp(self):
        self.s = Settings()

    def test_cad_stock_uses_estimated_spread_and_no_commission(self):
        a = self.s.asset("RY")
        q = {"price": 100.0, "bid": None, "ask": None}
        ex = costs.execution(self.s, a, q, "buy", 1)
        half = self.s["costs"]["questrade"]["estimated_spread_pct"]["large_cap"] / 2 * 100
        slip = self.s["costs"]["questrade"]["slippage_pct"]
        self.assertAlmostEqual(ex["price"], (100 + half) * (1 + slip))
        self.assertEqual(ex["commission_cad"], 0.0)
        self.assertEqual(ex["fx_fee_cad"], 0.0)
        self.assertEqual(ex["spread_source"], "estimated")

    def test_usd_stock_pays_fx_fee(self):
        a = self.s.asset("AAPL")
        ex = costs.execution(self.s, a, {"price": 200.0, "bid": 199.9, "ask": 200.1}, "buy", 2, usdcad=1.4)
        notional = 200.1 * (1 + self.s["costs"]["questrade"]["slippage_pct"]) * 2 * 1.4
        self.assertAlmostEqual(ex["notional_cad"], notional)
        self.assertAlmostEqual(ex["fx_fee_cad"], notional * 0.015)
        self.assertAlmostEqual(ex["cash_delta_cad"], -(notional * 1.015))
        with self.assertRaises(ValueError):
            costs.execution(self.s, a, {"price": 200.0}, "buy", 1)  # no FX rate -> refuse

    def test_crypto_taker_fee_and_sell_at_bid(self):
        a = self.s.asset("XBTCAD")
        ex = costs.execution(self.s, a, {"price": 90000, "bid": 89990, "ask": 90010}, "sell", 0.001)
        px = 89990 * (1 - self.s["costs"]["kraken"]["slippage_pct"])
        self.assertAlmostEqual(ex["price"], px)
        self.assertAlmostEqual(ex["venue_fee_cad"], px * 0.001 * 0.004)

    def test_whole_shares_only(self):
        self.assertEqual(costs.round_qty(self.s, self.s.asset("RY"), 2.9), 2.0)
        self.assertEqual(costs.round_qty(self.s, self.s.asset("XBTCAD"), 0.123456789), 0.12345678)


class PortfolioTests(unittest.TestCase):
    def test_round_trip_reconciles_with_fees(self):
        fills = [
            {"seq": 1, "trade_id": "t1", "symbol": "RY", "side": "buy", "qty": 2, "cash_delta_cad": -200.5, "fees_cad": 0.5, "filled_at": "x"},
            {"seq": 2, "trade_id": "t1", "symbol": "RY", "side": "sell", "qty": 1, "cash_delta_cad": 110.0, "fees_cad": 0.25, "filled_at": "y"},
        ]
        p = Portfolio.from_fills(1000, fills)
        self.assertAlmostEqual(p.cash, 909.5)
        self.assertAlmostEqual(p.realized["t1"], 110.0 - 100.25)
        self.assertTrue(p.reconcile()[0])
        eq, missing = p.equity({"RY": 105.0})
        self.assertAlmostEqual(eq, 909.5 + 105.0)
        self.assertEqual(missing, [])
        eq2, missing2 = p.equity({})
        self.assertEqual(missing2, ["RY"])  # never invents a price

    def test_cannot_oversell(self):
        with self.assertRaises(ValueError):
            Portfolio.from_fills(1000, [{"seq": 1, "trade_id": "t", "symbol": "RY", "side": "sell", "qty": 1,
                                         "cash_delta_cad": 10, "fees_cad": 0, "filled_at": "x"}])


class IndicatorTests(unittest.TestCase):
    def test_sma_ema_rsi(self):
        xs = list(range(1, 31))
        self.assertEqual(indicators.sma(xs, 5), 28)
        self.assertEqual(indicators.rsi(xs), 100.0)  # only gains
        down = list(range(30, 0, -1))
        self.assertAlmostEqual(indicators.rsi(down), 0.0)
        self.assertIsNone(indicators.sma(xs, 50))
        self.assertAlmostEqual(indicators.momentum(xs, 10), 30 / 20 - 1)


if __name__ == "__main__":
    unittest.main()
