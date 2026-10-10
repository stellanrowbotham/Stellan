"""Documented candidate scoring system (0-100). See settings.json["candidate_scoring"].

  evidence_quality (25): source tiers (A 1.0, B .85, C .7, D .3) x independent origins (3 = full marks)
  fundamentals     (20): agent's 0-1 judgement, must cite evidence
  technicals       (20): agent's 0-1 judgement, informed by computed indicators
  reward_risk      (20): (target-entry)/(entry-stop); 3:1 or better = full marks
  catalyst         (10): agent's 0-1 judgement of a dated, sourced catalyst
  freshness         (5): 1 - price age / strategy's allowed age

A candidate is tradeable only if total >= min_total_score AND reward:risk >= min_reward_risk AND
it has >= min_independent_sources independent origins including at least one tier A or B source.
A high score is not proof a trade will work."""
from .research import TIER_WEIGHT, independence
from .validate import age_minutes

NO_TRADE = "No trade: current opportunities do not meet the required criteria."


def score(settings, cand, evidence, quote, now):
    cfg = settings["candidate_scoring"]
    w = cfg["weights"]
    n_ind, tiers = independence(settings, evidence)
    top = sorted((TIER_WEIGHT[t] for t in tiers), reverse=True)[:3]
    ev_q = (sum(top) / len(top)) * min(n_ind, 3) / 3 if top else 0.0
    entry, stop, target = cand.get("entry_price"), cand.get("stop_price"), cand.get("target_price")
    rr = (target - entry) / (entry - stop) if (entry and stop and target and entry > stop) else 0.0
    strat = settings.strategy(cand.get("strategy", "swing")) or settings.strategy("swing")
    kind = "crypto" if cand.get("asset_type") == "crypto" else "stock"
    max_age = strat["max_research_price_age_hours"][kind] * 60
    age = age_minutes(quote, now) if quote else float("inf")
    fresh = max(0.0, 1 - age / max_age) if quote else 0.0
    clip = lambda x: max(0.0, min(1.0, float(x or 0)))
    parts = {
        "evidence_quality": ev_q, "fundamentals": clip(cand.get("fundamentals_score")),
        "technicals": clip(cand.get("technicals_score")), "reward_risk": min(rr / 3, 1.0),
        "catalyst": clip(cand.get("catalyst_score")), "freshness": fresh,
    }
    total = sum(w[k] * v for k, v in parts.items())
    gates = {
        "score": (total >= cfg["min_total_score"], f"score {total:.0f} (need {cfg['min_total_score']})"),
        "reward_risk": (rr >= cfg["min_reward_risk"], f"reward:risk {rr:.2f} (need {cfg['min_reward_risk']})"),
        "independent_sources": (n_ind >= cfg["min_independent_sources"], f"{n_ind} independent sources (need {cfg['min_independent_sources']})"),
        "primary_or_licensed": ((not cfg["require_primary_or_licensed_source"]) or any(t in ("A", "B") for t in tiers),
                                "has an official or licensed-data source" if any(t in ("A", "B") for t in tiers) else "no official/licensed source"),
        "price_fresh": (age <= max_age, f"price age {age:.0f} min (limit {max_age:.0f})" if quote else "no price"),
    }
    return {"total": round(total, 1), "parts": {k: round(v, 3) for k, v in parts.items()}, "reward_risk": round(rr, 2),
            "independent_sources": n_ind, "tiers": tiers, "gates": {k: {"passed": v[0], "detail": v[1]} for k, v in gates.items()},
            "tradeable": all(v[0] for v in gates.values())}
