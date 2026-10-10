import json
from pathlib import Path
import unittest
from datetime import timedelta
from unittest import mock

from apprentice import backtest, dashboard, forecasts, promotion, report, research, reviews, scoring
from apprentice.broker import PaperBroker
from apprentice.ledger import iso
from apprentice.providers import base as pbase
from apprentice.providers import sources as P
from apprentice.scorecard import totals

from .helpers import Env, et, proposal

T0 = et(2026, 10, 13, 10, 0)


class Base(unittest.TestCase):
    level = 2

    def setUp(self):
        self.env = Env(level=self.level)
        self.s = self.env.settings()
        self.b = PaperBroker(self.s, self.env.ledger)

    def tearDown(self):
        self.env.cleanup()


class ForecastTests(Base):
    def test_record_and_score(self):
        q = self.env.quote("XBTCAD", T0 - timedelta(minutes=1), bid=90000, ask=90010, exchange="KRAKEN", asset_type="crypto")
        n = self.env.note(T0 - timedelta(minutes=10), source_id="coindesk")
        rec, probs = forecasts.add(self.s, {"symbol": "XBTCAD", "direction": "up", "probability": 0.6, "horizon": "4h",
                                             "reference_quote_id": q["id"], "rationale": "Fictional", "evidence_ids": [n["id"]],
                                             "made_at": iso(T0)}, T0, self.env.ledger)
        self.assertEqual(probs, [])
        self.assertAlmostEqual(rec["reference_price"], 90005)
        self.assertEqual(forecasts.score_due(self.s, T0 + timedelta(hours=1), self.env.ledger), [])  # not due yet
        self.env.quote("XBTCAD", T0 + timedelta(hours=4, minutes=5), bid=91000, ask=91010, exchange="KRAKEN", asset_type="crypto")
        out = forecasts.score_due(self.s, T0 + timedelta(hours=5), self.env.ledger)
        self.assertEqual(out[0]["status"], "scored")
        self.assertTrue(out[0]["hit"])
        self.assertAlmostEqual(out[0]["brier"], (0.6 - 1) ** 2)
        # original forecast is untouched
        self.assertEqual(self.env.L("forecasts").read()[0]["probability"], 0.6)
        self.assertEqual(self.env.L("forecasts").verify(), [])

    def test_rejects_lookahead_and_overconfidence(self):
        q = self.env.quote("XBTCAD", T0 + timedelta(minutes=5), bid=90000, ask=90010, exchange="KRAKEN", asset_type="crypto")
        rec, probs = forecasts.add(self.s, {"symbol": "XBTCAD", "direction": "up", "probability": 0.99, "horizon": "4h",
                                             "reference_quote_id": q["id"], "rationale": "x", "evidence_ids": [q["id"]],
                                             "made_at": iso(T0)}, T0 + timedelta(minutes=10), self.env.ledger)
        self.assertIsNone(rec)
        self.assertTrue(any("probability" in p for p in probs))
        self.assertTrue(any("after decision" in p for p in probs))
        self.assertEqual(totals(self.env.L("scorecard").read())["timestamp_errors"], 1)

    def test_unscorable_when_no_price(self):
        q = self.env.quote("XBTCAD", T0 - timedelta(minutes=1), bid=90000, ask=90010, exchange="KRAKEN", asset_type="crypto")
        forecasts.add(self.s, {"symbol": "XBTCAD", "direction": "down", "probability": 0.55, "horizon": "1h",
                               "reference_quote_id": q["id"], "rationale": "x", "evidence_ids": [q["id"]]}, T0, self.env.ledger)
        out = forecasts.score_due(self.s, T0 + timedelta(hours=3), self.env.ledger)
        self.assertEqual(out[0]["status"], "unscorable")


class ResearchTests(Base):
    def test_unsourced_fact_rejected_and_penalized(self):
        added, rejected = research.add_notes(self.s, [{"kind": "note", "title": "RY will beat earnings", "claim_type": "fact"}], T0, self.env.ledger)
        self.assertEqual(added, [])
        self.assertEqual(totals(self.env.L("scorecard").read())["integrity_violations"], 1)

    def test_opinion_and_interpretation_allowed_and_labelled(self):
        h = self.env.note(T0 - timedelta(hours=1), source_id="cnbc")
        added, rejected = research.add_notes(self.s, [{"kind": "note", "title": "Banks look cheap vs history", "claim_type": "ai_interpretation",
                                                       "based_on": [h["id"]]}], T0, self.env.ledger)
        self.assertEqual(rejected, [])
        self.assertEqual(added[0]["claim_type"], "ai_interpretation")

    def test_syndicated_copies_are_one_source(self):
        a = {"id": "n1", "kind": "headline", "title": "Bank of Canada cuts rates!", "url": "https://a.invalid/1", "published_at": "2026-10-13T13:00:00Z",
             "norm_title": P._norm_title("Bank of Canada cuts rates!"), "source_id": "cnbc"}
        b = {"id": "n2", "kind": "headline", "title": "Bank of Canada cuts rates", "url": "https://b.invalid/2", "published_at": "2026-10-13T13:20:00Z",
             "norm_title": P._norm_title("Bank of Canada cuts rates"), "source_id": "yahoo_finance"}
        out = P.dedupe_headlines([b, a], [])
        self.assertEqual(out[1]["syndicated_from"], "n1")
        n, tiers = research.independence(self.s, out)
        self.assertEqual(n, 1)


class ReviewTests(Base):
    def _closed_trade(self):
        self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        ev = [self.env.note(T0 - timedelta(minutes=30))["id"]]
        r = self.b.propose(proposal("BCE", T0, ev, stop=39.2, target=42), T0)
        t1 = T0 + timedelta(days=1)
        self.env.quote("BCE", t1 - timedelta(minutes=1), bid=42.5, ask=42.55)
        self.b.process(t1)
        return r["trade_id"], t1

    def test_complete_review_uses_recorded_outcome(self):
        tid, t1 = self._closed_trade()
        answers = {k: "A sufficiently detailed fictional test answer." for k in reviews.QUESTIONS}
        rec, probs = reviews.add(self.s, self.b, {"trade_id": tid, "answers": answers, "verdict": "sound_process",
                                                  "thesis_correct": True, "lessons": ["fictional lesson"]}, t1)
        self.assertEqual(probs, [])
        trade = self.b.trades()[tid]
        self.assertEqual(rec["original_thesis"], "Fictional test thesis")
        self.assertAlmostEqual(rec["realized_pnl_cad"], trade["exit"]["realized_pnl_cad"])
        self.assertTrue(rec["rule_compliance"]["all"])
        self.assertEqual(totals(self.env.L("scorecard").read())["points"], 3)
        self.assertEqual(reviews.due(self.b), [])

    def test_incomplete_review_penalized(self):
        tid, t1 = self._closed_trade()
        rec, probs = reviews.add(self.s, self.b, {"trade_id": tid, "answers": {"hypothesis": "short"}, "verdict": "x"}, t1)
        self.assertTrue(probs)
        self.assertFalse(rec["complete"])
        self.assertLess(totals(self.env.L("scorecard").read())["points"], 0)


class PromotionTests(Base):
    level = 1

    def test_level1_explains_each_failure(self):
        ev = promotion.evaluate(self.s, self.b, T0)
        self.assertFalse(ev["eligible"])
        names = {c["name"]: c for c in ev["criteria"]}
        self.assertIn("observation_period", names)
        self.assertIn("forecasts_scored", names)
        self.assertFalse(names["forecasts_scored"]["passed"])
        self.assertTrue(all(c["explanation"] for c in ev["criteria"]))

    def test_level1_eligible_after_requirements_but_level_unchanged(self):
        t = T0
        for i in range(50):
            q = self.env.quote("XBTCAD", t, bid=90000 + i, ask=90010 + i, exchange="KRAKEN", asset_type="crypto")
            forecasts.add(self.s, {"symbol": "XBTCAD", "direction": "up", "probability": 0.6, "horizon": "1h",
                                   "reference_quote_id": q["id"], "rationale": "fictional", "evidence_ids": [q["id"]]}, t, self.env.ledger)
            t += timedelta(hours=1, minutes=5)
        self.env.quote("XBTCAD", t, bid=95000, ask=95010, exchange="KRAKEN", asset_type="crypto")
        later = et(2026, 11, 20, 10)
        forecasts.score_due(self.s, later, self.env.ledger)
        ev = promotion.evaluate(self.s, self.b, later)
        self.assertTrue(ev["eligible"], [c for c in ev["criteria"] if not c["passed"]])
        self.assertEqual(self.b.level(), 1)  # eligible is not promoted: needs Stellan

    def test_integrity_violation_blocks(self):
        research.add_notes(self.s, [{"kind": "note", "title": "made-up fact", "claim_type": "fact"}], T0, self.env.ledger)
        ev = promotion.evaluate(self.s, self.b, T0)
        self.assertFalse({c["name"]: c for c in ev["criteria"]}["no_fabrication"]["passed"])


class DemotionTests(Base):
    def test_drawdown_demotes_and_stops_trading(self):
        self.env.L("valuations").append({"at": iso(T0 - timedelta(days=2)), "equity": 1000.0, "cash": 1000.0}, now=T0)
        self.env.L("fills").append({"trade_id": "tx", "symbol": "BCE", "side": "buy", "qty": 1, "cash_delta_cad": -300.0, "fees_cad": 0,
                                    "filled_at": iso(T0)}, now=T0)
        self.env.L("fills").append({"trade_id": "tx", "symbol": "BCE", "side": "sell", "qty": 1, "cash_delta_cad": 120.0, "fees_cad": 0,
                                    "filled_at": iso(T0)}, now=T0)
        self.b.snapshot(T0 + timedelta(minutes=1))
        self.assertEqual(self.b.level(), 1)


class ScoringAndReport(Base):
    def test_no_trade_when_nothing_passes(self):
        q = self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        cand = {"symbol": "BCE", "name": "BCE Inc.", "quote_id": q["id"], "evidence_ids": [], "entry_price": 40.02,
                "stop_price": 39.0, "target_price": 41.0, "strategy": "swing"}
        rec, md, html = report.build(self.s, self.b, {"candidates": [cand], "sources_searched": ["fictional"]}, T0, "pre_market")
        self.assertTrue(rec["no_trade"])
        self.assertIn(scoring.NO_TRADE, md.read_text())
        self.assertIn("why it's being considered", rec["candidates"][0]["missing"])
        self.assertTrue(html.read_text().startswith("<html>"))

    def test_score_gates(self):
        q = self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
        ev = [self.env.note(T0 - timedelta(hours=1), source_id="sec_edgar"), self.env.note(T0 - timedelta(hours=1), source_id="cnbc", title="Other story")]
        s = scoring.score(self.s, {"entry_price": 40, "stop_price": 39, "target_price": 43.5, "fundamentals_score": 0.8,
                                   "technicals_score": 0.7, "catalyst_score": 0.6, "strategy": "swing"}, ev, q, T0)
        self.assertEqual(s["independent_sources"], 2)
        self.assertAlmostEqual(s["reward_risk"], 3.5)
        self.assertTrue(s["tradeable"], s["gates"])
        s2 = scoring.score(self.s, {"entry_price": 40, "stop_price": 39, "target_price": 41, "fundamentals_score": 1,
                                    "technicals_score": 1, "catalyst_score": 1}, ev, q, T0)
        self.assertFalse(s2["gates"]["reward_risk"]["passed"])

    def setUp(self):
        super().setUp()
        self._old = report.REPORT_DIR
        report.REPORT_DIR = self.env.root / "reports"

    def tearDown(self):
        report.REPORT_DIR = self._old
        super().tearDown()


class DashboardMatchesLedger(Base):
    def test_numbers_reconcile(self):
        old_out, old_exp = dashboard.OUT, dashboard.EXPORTS
        dashboard.OUT, dashboard.EXPORTS = self.env.root / "dash", self.env.root / "exp"
        try:
            self.env.quote("BCE", T0 - timedelta(minutes=2), bid=40.0, ask=40.02)
            self.b.propose(proposal("BCE", T0, [self.env.note(T0 - timedelta(minutes=30))["id"]], stop=39.2, target=42), T0)
            self.b.process(T0 + timedelta(minutes=5))
            paths = dashboard.export(self.s, self.b, T0 + timedelta(minutes=6))
            ov = json.loads(Path(paths["overview"]).read_text())
            port = self.b.portfolio()
            self.assertAlmostEqual(ov["cash"], round(port.cash, 2))
            self.assertEqual(len(ov["positions"]), len(port.positions))
            self.assertAlmostEqual(ov["equity"], round(port.cash + 2 * 40.0, 2))
            st = json.loads(Path(paths["settings"]).read_text())
            self.assertFalse(st["permissions"]["liveTrading"])
            self.assertEqual(len(st["sources"]), len(self.s.sources))
        finally:
            dashboard.OUT, dashboard.EXPORTS = old_out, old_exp


class ProviderTests(unittest.TestCase):
    def test_missing_keys_reported_not_faked(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            for fn, arg in ((P.coingecko, ["bitcoin"]), (P.fred, ()), (P.twelve_data_quotes, []), (P.alpha_vantage_quotes, []),
                            (P.finnhub_quotes, [])):
                r = fn(arg) if arg != () else fn()
                self.assertEqual(r.status, "needs-key")
                self.assertEqual(r.records, [])

    def test_network_block_reported(self):
        with mock.patch.object(P, "http_json", side_effect=pbase.FetchError("blocked-by-network", "policy blocked api.kraken.com")):
            r = P.kraken(["XBTCAD"])
        self.assertEqual(r.status, "blocked-by-network")
        self.assertEqual(r.records, [])

    def test_kraken_parsing(self):
        meta = {"error": [], "result": {"XXBTZCAD": {"altname": "XBTCAD"}}}
        tick = {"error": [], "result": {"XXBTZCAD": {"a": ["90010.0", "1", "1"], "b": ["90000.0", "1", "1"], "c": ["90005.0", "0.1"], "v": ["1", "2"]}}}
        with mock.patch.object(P, "http_json", side_effect=[meta, tick]):
            r = P.kraken(["XBTCAD"])
        self.assertEqual(r.status, "ok")
        self.assertEqual((r.records[0]["bid"], r.records[0]["ask"]), (90000.0, 90010.0))

    def test_rss_parse(self):
        xml = b"""<rss><channel><item><title>Fictional headline</title><link>https://x.invalid/a</link>
        <pubDate>Tue, 13 Oct 2026 13:00:00 GMT</pubDate></item></channel></rss>"""
        recs = P.parse_feed(xml, "cnbc")
        self.assertEqual(recs[0]["published_at"], "2026-10-13T13:00:00Z")


class BacktestTests(unittest.TestCase):
    def test_strategy_never_sees_future_bars(self):
        bars = [{"close": 100 + i} for i in range(200)]  # FICTIONAL series
        seen = []

        def spy(hist, p):
            seen.append(len(hist))
            return None

        backtest.run(bars, spy, {}, 0.001, 10, 20)
        self.assertEqual(seen, list(range(11, 21)))

    def test_walk_forward_reports_folds_with_costs(self):
        bars = [{"close": 100 + (i % 20)} for i in range(260)]  # FICTIONAL
        r = backtest.walk_forward(bars, backtest.sma_cross, [{"fast": 5, "slow": 20}, {"fast": 10, "slow": 40}], 0.002)
        self.assertGreater(r["n"], 0)
        self.assertTrue(all("oos_return" in f for f in r["folds"]))


if __name__ == "__main__":
    unittest.main()
