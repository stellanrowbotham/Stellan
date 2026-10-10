"""Post-trade reviews. Facts (prices, P&L, whether rules were followed) are filled in by code from
the ledger; the agent answers the eight questions. The original thesis is quoted from the trade
record and can't be rewritten."""
from . import scorecard
from .ledger import Ledger, iso, new_id

QUESTIONS = {
    "hypothesis": "What was the original hypothesis?",
    "evidence": "What evidence supported the decision?",
    "what_happened": "What happened afterward?",
    "assumptions": "Which assumptions were correct or incorrect?",
    "process_luck_mistake": "Did the result reflect a sound process, luck, or an identifiable mistake?",
    "rules_followed": "Were the entry, position size, and exit consistent with the rules?",
    "test_next_time": "What should be tested differently next time?",
    "change_strategy": "Is there enough evidence to change the strategy?",
}
VERDICTS = {"sound_process", "luck", "mistake"}
PLANNED_EXITS = {"stop", "target", "time", "end_of_day"}


def rule_compliance(trade):
    """Computed from the record, not self-reported."""
    entry_ok = all(c["passed"] for c in trade.get("risk_checks", []))
    exit_reason = trade.get("exit", {}).get("exit_reason")
    exit_ok = exit_reason in PLANNED_EXITS or exit_reason == "thesis_invalidated"
    return {"entry_and_size_within_rules": entry_ok, "exit_followed_plan": exit_ok, "exit_reason": exit_reason,
            "stop_gapped": trade.get("exit", {}).get("stop_gap", False), "all": entry_ok and exit_ok}


def due(broker):
    done = {r["trade_id"] for r in Ledger("reviews", **({"directory": broker.dir} if broker.dir else {})).read()}
    return [t for t in broker.trades().values() if t["status"] == "closed" and t["trade_id"] not in done]


def add(settings, broker, review, now):
    kw = {"directory": broker.dir} if broker.dir else {}
    t = broker.trades().get(review.get("trade_id"))
    if not t or t["status"] != "closed":
        return None, ["review needs a closed trade_id"]
    answers = review.get("answers", {})
    missing = [k for k in QUESTIONS if len(str(answers.get(k, "")).strip()) < 20]
    verdict = review.get("verdict")
    problems = [f"answer '{QUESTIONS[k]}' (20+ characters)" for k in missing]
    if verdict not in VERDICTS:
        problems.append(f"verdict must be one of {sorted(VERDICTS)}")
    if review.get("thesis_correct") not in (True, False, "partly"):
        problems.append("thesis_correct must be true, false or 'partly'")
    comp = rule_compliance(t)
    complete = not problems
    rec = Ledger("reviews", **kw).append({
        "id": new_id("rv"), "trade_id": t["trade_id"], "symbol": t["symbol"], "strategy": t["strategy"],
        "original_thesis": t["thesis"], "original_invalidation": t["invalidation"], "decided_at": t["decided_at"],
        "entry_price": t["entry"]["entry_price"], "exit_price": t["exit"]["exit_price"],
        "realized_pnl_cad": t["exit"]["realized_pnl_cad"], "return_pct": t["exit"]["return_pct"],
        "holding_days": t["exit"]["holding_days"], "exit_reason": t["exit"]["exit_reason"],
        "rule_compliance": comp, "answers": answers, "verdict": verdict, "thesis_correct": review.get("thesis_correct"),
        "lessons": review.get("lessons", []), "mistakes": review.get("mistakes", []), "complete": complete,
        "problems": problems}, now=now)
    if complete:
        scorecard.award(settings, "complete_post_trade_review", f"review of {t['symbol']}", rec["id"], broker.dir, now)
        if comp["all"]:
            scorecard.award(settings, "followed_all_rules_on_closed_trade", f"{t['symbol']} followed every rule", rec["id"], broker.dir, now)
    else:
        scorecard.award(settings, "incomplete_review", "; ".join(problems), rec["id"], broker.dir, now)
    return rec, problems
