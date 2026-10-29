import unittest
from unittest import mock

from apprentice import lab

# FICTIONAL price series for testing only
def series(n, f):
    return [f(i) for i in range(n)]


class LabTests(unittest.TestCase):
    def test_sma_matches_naive(self):
        xs = series(300, lambda i: 100 + (i % 17) - i * 0.1)
        for i in (49, 120, 299):
            self.assertAlmostEqual(lab._sma(xs, i, 50), sum(xs[i - 49:i + 1]) / 50)
        self.assertIsNone(lab._sma(xs, 10, 50))

    def test_no_lookahead_signal_earns_next_day(self):
        # price jumps on day 300; a trend rule can't capture the jump that created its own signal
        xs = series(310, lambda i: 100.0 if i < 300 else 200.0)
        closes = {"A": xs}
        r, _, _ = lab.simulate("trend", {"n": 50}, closes, 250, 305, 0.0)
        self.assertAlmostEqual(sum(r), 0.0)  # flat below/at SMA before the jump -> not holding on the jump day

    def test_costs_charged_on_turnover(self):
        xs = series(400, lambda i: 100 + i)  # steady uptrend: buy once and hold
        r, turnover, trades = lab.simulate("trend", {"n": 50}, {"A": xs}, 100, 300, 0.01)
        self.assertEqual(trades, 1)
        self.assertAlmostEqual(turnover, 1.0)

    def test_walk_forward_reports_oos_only(self):
        xs = series(1600, lambda i: 100 * (1.0005 ** i) * (1 + 0.05 * ((i // 60) % 2)))
        closes = {"A": xs, "B": [x * 0.5 for x in xs]}
        res = lab.walk_forward("trend", closes, "us", train_years=2, test_years=1)
        self.assertGreaterEqual(res["folds"], 2)
        self.assertIn("passes", res)
        self.assertTrue(all(f["test_days"][0] >= 260 + 2 * 252 for f in res["fold_detail"]))

    def test_momentum_buffer_keeps_winner_inside_buffer(self):
        up = series(600, lambda i: 100 * 1.002 ** i)
        closes = {"A": up, "B": series(600, lambda i: 100 * 1.0015 ** i), "C": series(600, lambda i: 100 * 1.001 ** i)}
        p = {"lookback": 126, "top": 1, "buffer": 3, "exit_sma": 50, "every": 5}
        held = lab.weights("momentum_buffer", p, closes, 400)
        self.assertEqual(set(held), {"A"})
        closes["B"] = [x * (1 + 0.01 * (i - 380)) if i > 380 else x for i, x in enumerate(closes["B"])]  # B overtakes A
        again = lab.weights("momentum_buffer", p, closes, 420, held=held)
        self.assertEqual(set(again), {"A"})  # A is still in the top 3 and above its average: no churn

    def test_rsi2_buys_dip_in_uptrend_and_sells_on_recovery(self):
        xs = series(400, lambda i: 100 + i * 0.5)
        xs[300], xs[301] = xs[299] - 3, xs[299] - 6  # two-day panic inside an uptrend
        p = {"entry": 10, "exit": 70, "slots": 1}
        w = lab.weights("rsi2", p, {"A": xs}, 301, held={})
        self.assertIn("A", w)
        xs[302], xs[303] = xs[301] + 5, xs[301] + 10
        self.assertEqual(lab.weights("rsi2", p, {"A": xs}, 303, held=w), {})

    def test_current_matches_simulation_memory(self):
        xs = series(700, lambda i: 100 * 1.001 ** i * (1 + 0.03 * ((i // 40) % 2)))
        closes = {"A": xs, "B": [x * 0.7 for x in reversed(xs)]}
        p = {"lookback": 126, "top": 1, "buffer": 2, "exit_sma": 50, "every": 5}
        self.assertTrue(set(lab.current("momentum_buffer", p, closes)) <= {"A", "B"})

    def test_us_costs_include_currency_conversion(self):
        self.assertGreaterEqual(lab.COST["us"], 0.015)


if __name__ == "__main__":
    unittest.main()
