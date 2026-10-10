"""Risk engine. Plain code, not AI judgement. Every simulated entry passes through check_entry();
any failed check rejects the order. The AI cannot change these limits (they live in the protected,
hash-checked settings.json) and an unapproved config locks trading entirely."""
from datetime import timedelta

from . import LIVE_TRADING_AVAILABLE
from .ledger import parse_ts
from .market_calendar import ET
from .validate import age_minutes, lookahead_violations, quote_problems


class Check:
    __slots__ = ("name", "passed", "detail")

    def __init__(self, name, passed, detail):
        self.name, self.passed, self.detail = name, bool(passed), detail

    def as_dict(self):
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


def halt_state(valuations, equity_now, now, settings):
    """(halted_today, drawdown_review, info). Uses the valuation history."""
    r = settings.risk
    today = now.astimezone(ET).date()
    before = [v for v in valuations if parse_ts(v["at"]).astimezone(ET).date() < today]
    todays = [v for v in valuations if parse_ts(v["at"]).astimezone(ET).date() == today]
    start_of_day = (todays[0]["equity"] if todays else before[-1]["equity"] if before else settings["account"]["starting_balance"])
    peak = max([v["equity"] for v in valuations] + [settings["account"]["starting_balance"], equity_now])
    day_change = equity_now / start_of_day - 1
    drawdown = equity_now / peak - 1
    return (day_change <= -r["daily_loss_halt_pct"], drawdown <= -r["drawdown_review_pct"],
            {"start_of_day": start_of_day, "day_change": day_change, "peak": peak, "drawdown": drawdown})


def check_entry(*, settings, level, proposal, asset, quote, usdcad, portfolio, marks, valuations, evidence,
                known_ids, now, qty, est_cost_cad, est_price):
    """Return a list of Check objects. The order is accepted only if all pass."""
    r = settings.risk
    checks = []
    add = lambda n, ok, d: checks.append(Check(n, ok, d))
    strat = settings.strategy(proposal.get("strategy", ""))

    add("simulation_only", not LIVE_TRADING_AVAILABLE and not settings["live_trading"]["enabled"],
        "Simulation only: no live-trading code exists.")
    add("config_approved", settings.approved,
        "Config matches Stellan's approved hash." if settings.approved else "Config changed without approval: all trading locked.")
    add("asset_approved", asset is not None, f"{proposal.get('symbol')} is in the approved universe." if asset else
        f"{proposal.get('symbol')} is not in the approved universe.")
    if asset is None:
        return checks
    banned = set(asset.get("tags", [])) & set(r["banned_tags"])
    add("asset_not_banned", not banned, "Not leveraged, inverse, penny or OTC." if not banned else f"Banned type: {sorted(banned)}")
    add("strategy_enabled", bool(strat and strat.get("enabled")), f"Strategy '{proposal.get('strategy')}' is enabled."
        if strat and strat.get("enabled") else f"Strategy '{proposal.get('strategy')}' is unknown or disabled.")
    if not strat:
        return checks
    add("level_permits_trading", level >= strat["min_level"],
        f"Level {level} may trade this strategy (needs {strat['min_level']})." if level >= strat["min_level"] else
        f"Level {level} cannot place simulated trades yet (needs level {strat['min_level']}). Forecasts only.")
    add("long_only", proposal.get("side", "buy") == "buy" or not r["long_only"], "Long-only: buys to open.")

    stop, target = proposal.get("stop_price"), proposal.get("target_price")
    ok_stop = (stop is not None and 0 < stop < est_price) if r["require_stop"] else True
    add("stop_loss_set", ok_stop, f"Stop {stop} below entry {est_price:.4f}." if ok_stop else "A stop-loss below the entry price is required.")
    add("target_set", target is not None and target > est_price, f"Target {target} above entry." if target and target > est_price
        else "A profit target above the entry price is required.")

    qp = quote_problems(quote, now) if quote else ["no quote"]
    add("quote_valid", not qp, "Quote passed validation." if not qp else "; ".join(qp))
    if quote:
        max_age = strat["max_research_price_age_hours"]["crypto" if asset["asset_type"] == "crypto" else "stock"] * 60
        age = age_minutes(quote, now)
        add("price_fresh_enough", age <= max_age, f"Price is {age:.0f} min old (limit {max_age:.0f} for {strat['label']}).")
    if asset["currency"] == "USD":
        add("fx_rate_available", bool(usdcad), "USD/CAD rate available." if usdcad else "No USD/CAD rate: cannot price a US asset in CAD.")

    ev_ids = proposal.get("evidence_ids") or []
    missing = [i for i in ev_ids if i not in known_ids]
    add("evidence_recorded", bool(ev_ids) and not missing, f"{len(ev_ids)} evidence records cited." if ev_ids and not missing
        else ("No evidence cited." if not ev_ids else f"Cited evidence not in the ledger: {missing}"))
    la = lookahead_violations(proposal.get("decided_at"), evidence)
    add("no_lookahead", not la, "All evidence predates the decision." if not la else "; ".join(la[:3]))
    for f in ("thesis", "invalidation", "exit_rules"):
        add(f"has_{f}", bool(proposal.get(f)), f"{f} recorded." if proposal.get(f) else f"Missing {f}.")

    equity, _ = portfolio.equity(marks)
    halted, dd_review, info = halt_state(valuations, equity, now, settings)
    add("daily_loss_halt", not halted, f"Today {info['day_change']:+.2%} (halt at -{r['daily_loss_halt_pct']:.0%}).")
    add("drawdown_review", not dd_review, f"Drawdown {info['drawdown']:+.2%} from peak (review at -{r['drawdown_review_pct']:.0%}).")
    add("max_open_positions", len(portfolio.positions) < r["max_open_positions"],
        f"{len(portfolio.positions)} open (max {r['max_open_positions']}).")

    add("quantity_positive", qty > 0, f"Quantity {qty}." if qty > 0 else
        "Position rounds to zero units (whole shares only, or below the minimum order).")
    if qty <= 0:
        return checks
    pos_value = est_cost_cad
    add("position_size", pos_value <= r["max_position_pct"] * equity + 1e-9,
        f"${pos_value:.2f} = {pos_value / equity:.1%} of ${equity:.2f} (max {r['max_position_pct']:.0%}).")
    if stop is not None and stop < est_price:
        fx = usdcad if asset["currency"] == "USD" else 1.0
        risk_cad = (est_price - stop) * qty * (fx or 1.0)
        add("risk_per_trade", risk_cad <= r["max_risk_per_trade_pct"] * equity + 1e-9,
            f"Loss to stop ${risk_cad:.2f} = {risk_cad / equity:.2%} (max {r['max_risk_per_trade_pct']:.0%}).")
    sectors, crypto = portfolio.exposure(marks, settings)
    sec = asset.get("sector", "unknown")
    after = sectors.get(sec, 0.0) + pos_value
    if asset["asset_type"] != "crypto":
        add("sector_limit", after <= r["max_sector_pct"] * equity + 1e-9,
            f"{sec}: ${after:.2f} = {after / equity:.1%} after trade (max {r['max_sector_pct']:.0%}).")
    if asset["asset_type"] == "crypto":
        c_after = crypto + pos_value
        add("crypto_limit", c_after <= r["max_crypto_pct"] * equity + 1e-9,
            f"Crypto ${c_after:.2f} = {c_after / equity:.1%} after trade (max {r['max_crypto_pct']:.0%}).")
        mn = settings["costs"]["kraken"]["min_order_value"]
        add("min_order_value", pos_value >= mn, f"Order ${pos_value:.2f} (min ${mn}).")
    add("cash_available", est_cost_cad <= portfolio.cash + 1e-9, f"Needs ${est_cost_cad:.2f}, cash ${portfolio.cash:.2f}.")
    return checks


def size_position(*, settings, asset, est_price, stop, equity, cash, usdcad, round_qty, cost_factor):
    """Largest quantity allowed by position, risk and cash limits."""
    r = settings.risk
    fx = usdcad if asset["currency"] == "USD" else 1.0
    unit_cad = est_price * fx * cost_factor
    caps = [r["max_position_pct"] * equity / unit_cad, cash / unit_cad]
    if stop is not None and stop < est_price:
        caps.append(r["max_risk_per_trade_pct"] * equity / ((est_price - stop) * fx))
    return max(round_qty(settings, asset, min(caps)), 0.0)
