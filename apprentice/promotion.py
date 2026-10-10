"""Promotion and demotion evaluation. Results say exactly which requirement passed or failed and
why. A pass makes the agent *eligible*; only Stellan's approval of a config change promotes it."""
from datetime import datetime, time

from . import forecasts as fc
from . import metrics, scorecard
from .ledger import Ledger, iso, new_id, parse_ts
from .levels import NAMES, effective_level
from .market_calendar import ET, trading_days_between
from .quotebook import QuoteBook
from .settings import config_hash


def _crit(name, required, actual, passed, why):
    return {"name": name, "required": required, "actual": actual, "passed": bool(passed), "explanation": why}


def evaluate(settings, broker, now, write=True):
    kw = {"directory": broker.dir} if broker.dir else {}
    L = lambda n: Ledger(n, **kw).read()
    level = effective_level(settings, L("level_events"))
    rules = settings["promotion"].get(str(level), {})
    start = datetime.fromisoformat(settings["account"]["start_date"]).date()
    days = trading_days_between("TSX", start, now.astimezone(ET).date())
    cal_days = (now.astimezone(ET).date() - start).days
    sc = scorecard.totals(L("scorecard"))
    fstats = fc.stats(L("forecasts"), L("forecast_scores"))
    trades = broker.trades()
    closed = [t for t in trades.values() if t["status"] == "closed"]
    reviews = {r["trade_id"]: r for r in L("reviews")}
    vals = L("valuations")
    crit = []
    if rules.get("to") is None:
        crit.append(_crit("top_level", "-", level, False, "Level 5 is the top. It never unlocks real money."))
    if "min_trading_days" in rules:
        crit.append(_crit("observation_period", f">= {rules['min_trading_days']} trading days", days,
                          days >= rules["min_trading_days"], f"{days} TSX trading days since {start}."))
    if "min_calendar_days" in rules:
        crit.append(_crit("observation_period", f">= {rules['min_calendar_days']} days", cal_days,
                          cal_days >= rules["min_calendar_days"], f"{cal_days} days since {start}."))
    if "min_forecasts_scored" in rules:
        n = fstats.get("scored", 0)
        crit.append(_crit("forecasts_scored", f">= {rules['min_forecasts_scored']}", n, n >= rules["min_forecasts_scored"],
                          f"{n} forecasts have been scored against real prices."))
    if "min_forecast_completeness" in rules:
        fs = L("forecasts")
        comp = (sum(1 for f in fs if f.get("complete")) / len(fs)) if fs else 0.0
        crit.append(_crit("complete_research_records", f">= {rules['min_forecast_completeness']:.0%}", f"{comp:.0%}",
                          fs and comp >= rules["min_forecast_completeness"], "Share of forecasts with every required field and evidence."))
    if "max_integrity_violations" in rules:
        crit.append(_crit("no_fabrication", f"<= {rules['max_integrity_violations']}", sc["integrity_violations"],
                          sc["integrity_violations"] <= rules["max_integrity_violations"],
                          "Made-up or unsourced facts and timestamp errors recorded on the scorecard."))
    if "max_timestamp_errors" in rules:
        crit.append(_crit("accurate_timestamps", f"<= {rules['max_timestamp_errors']}", sc["timestamp_errors"],
                          sc["timestamp_errors"] <= rules["max_timestamp_errors"], "Evidence dated after a decision, or future timestamps."))
    if "min_closed_trades" in rules:
        crit.append(_crit("closed_trades", f">= {rules['min_closed_trades']}", len(closed), len(closed) >= rules["min_closed_trades"],
                          f"{len(closed)} simulated trades completed."))
    if "max_risk_violations" in rules:
        crit.append(_crit("risk_controls", f"<= {rules['max_risk_violations']}", sc["risk_violations"],
                          sc["risk_violations"] <= rules["max_risk_violations"], "Attempts to break a risk limit (all were blocked)."))
    if "min_review_completeness" in rules:
        comp = (sum(1 for t in closed if reviews.get(t["trade_id"], {}).get("complete")) / len(closed)) if closed else 0.0
        crit.append(_crit("post_trade_reviews", f">= {rules['min_review_completeness']:.0%}", f"{comp:.0%}",
                          closed and comp >= rules["min_review_completeness"], "Closed trades with a complete review."))
    if "max_drawdown_pct" in rules:
        mdd = metrics.max_drawdown([settings["account"]["starting_balance"]] + [v["equity"] for v in vals])
        crit.append(_crit("drawdown", f"> -{rules['max_drawdown_pct']:.0%}", f"{mdd:.1%}", mdd > -rules["max_drawdown_pct"],
                          "Largest fall from a peak in account value."))
    if "max_single_trade_profit_share" in rules:
        share = metrics.trade_stats(closed).get("largest_profit_share")
        crit.append(_crit("not_one_lucky_trade", f"<= {rules['max_single_trade_profit_share']:.0%}",
                          "n/a" if share is None else f"{share:.0%}", share is not None and share <= rules["max_single_trade_profit_share"],
                          "The biggest winner's share of all winning profit."))
    if rules.get("must_beat_benchmark_after_costs"):
        ordered = sorted(closed, key=lambda t: t["exit"]["exit_at"])
        k = max(1, int(len(ordered) * rules["holdout_fraction"])) if ordered else 0
        hold = ordered[-k:] if k else []
        book = QuoteBook(broker.dir)
        if hold:
            t0 = parse_ts(hold[0]["decided_at"])
            strat_ret = sum(t["exit"]["realized_pnl_cad"] for t in hold) / settings["account"]["starting_balance"]
            bench = metrics.benchmark_return(book, settings["benchmarks"]["CA_STOCK"]["symbol"], t0, now)
            ok = bench is not None and strat_ret > bench
            crit.append(_crit("beats_benchmark_out_of_sample", "held-out return > XIU", f"{strat_ret:.2%} vs {'n/a' if bench is None else f'{bench:.2%}'}",
                              ok, f"Last {len(hold)} trades (held-out third), after all costs."))
        else:
            crit.append(_crit("beats_benchmark_out_of_sample", "held-out return > XIU", "no trades", False, "No held-out trades yet."))
    if "min_market_regimes" in rules:
        eq = metrics.daily_equity(vals)
        months = {}
        for d, e in eq:
            months.setdefault((d.year, d.month), []).append(e)
        regimes = {("up" if v[-1] >= v[0] else "down") for v in months.values() if len(v) > 1}
        crit.append(_crit("market_regimes", f">= {rules['min_market_regimes']}", len(regimes), len(regimes) >= rules["min_market_regimes"],
                          "Distinct up/down months the agent traded through."))
    eligible = bool(crit) and all(c["passed"] for c in crit) and rules.get("to") is not None
    demotion = _demotion_checks(settings, level, sc, fstats)
    result = {"id": new_id("ev"), "at": iso(now), "level": level, "level_name": NAMES[level],
              "next_level": rules.get("to"), "next_level_name": NAMES.get(rules.get("to")), "criteria": crit, "eligible": eligible,
              "note": ("Eligible: waiting for Stellan's approval. Promotion only happens when he approves a config change."
                       if eligible else "Not yet eligible. See each requirement."),
              "demotion_flags": demotion, "scorecard": sc}
    if write:
        Ledger("evaluations", **kw).append(result, now=now)
        h = config_hash(settings.config_dir)
        for flag in demotion:
            if flag["demote"] and level >= 2 and not any(e.get("reason_code") == flag["code"] and e.get("config_hash") == h for e in L("level_events")):
                Ledger("level_events", **kw).append({"event": "demotion", "from_level": level, "to_level": level - 1, "reason_code": flag["code"],
                                                     "reason": flag["detail"], "config_hash": h}, now=now)
    return result


def _demotion_checks(settings, level, sc, fstats):
    d = settings["promotion"]["demotion"]
    flags = []
    if d.get("integrity_violation") and sc["integrity_violations"] > 0:
        flags.append({"code": "integrity", "demote": True, "detail": f"{sc['integrity_violations']} integrity violation(s): promotion blocked, supervised level."})
    b = fstats.get("brier_last30")
    if b is not None and fstats.get("scored", 0) >= 30 and b > d["rolling_brier_worse_than"]:
        flags.append({"code": "forecast_quality", "demote": True, "detail": f"Last-30 Brier {b:.3f} is worse than {d['rolling_brier_worse_than']}."})
    return flags
