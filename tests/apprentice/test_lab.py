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


if __name__ == "__main__":
    unittest.main()
