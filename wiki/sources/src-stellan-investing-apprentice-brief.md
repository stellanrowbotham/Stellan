---
type: source
title: Stellan's brief for an AI investing apprentice
aliases: ["Investing apprentice brief", "Apprentice spec"]
tags: [investing, agents]
created: 2026-10-10
updated: 2026-10-10
sources: []
raw: raw/2026-10-10-investing-apprentice-brief.md
---

# Stellan's brief for an AI investing apprentice
> **Raw:** `raw/2026-10-10-investing-apprentice-brief.md` · **Author:** Stellan Rowbotham · **Published:** 2026-10-10 · **Ingested:** 2026-10-10

## TL;DR
A specification for a personal AI agent that researches stocks and crypto, makes **simulated** trades only, tracks results honestly, learns from its mistakes, and earns promotions through five levels using measurable evidence. It also lists 45 approved research sources. Real-money trading is out of scope, and a separate approval process would be needed for it.

## Key points
- **Interview first.** No building until Stellan approves a plan.
- **Research engine:** prices, news, fundamentals, technical indicators, macro data, crypto on-chain/supply data and upcoming events. Every claim needs a source with a timestamp. It must never invent data, and must say when the evidence is thin. See [[source-reliability]].
- **Daily report:** each candidate gets entry, exit, stop, size, scenarios and an evidence-based confidence level. The report may say "No trade: current opportunities do not meet the required criteria."
- **Paper trading:** real prices with realistic fees, spreads and slippage ([[trading-costs]]), plus market hours, and no [[look-ahead-bias]]. Each trade keeps its original thesis forever. See [[paper-trading]].
- **Learning:** an 8-question post-trade review, a research journal and a versioned strategy library. Changes are tested out-of-sample before adoption. The agent may not edit its own safeguards or evaluation rules.
- **Promotions:** Level 1 Research Apprentice → 2 Paper-Trading Apprentice → 3 Research Analyst → 4 Senior Analyst → 5 Trusted Research Agent. Thresholds are configurable, promotions that change permissions need human approval, and a short burst of high returns never earns a promotion. See [[promotion-system]].
- **Rewards and penalties:** rewards go to discipline, accurate records and risk control, not to activity. Penalties cover fabrication, rule breaks and integrity violations. See [[risk-management]].
- **Live trading:** separate module, off by default. It would require a risk briefing, verified performance, human approval of each exact trade, a kill switch, an audit log and the ability to revoke access.
- **Dashboard tabs:** Overview, Research, Paper Trading, Learning Center, Progression and Settings. No fake numbers.
- **Source library:** 45 sources in 6 groups (journalism, disclosures and exchanges, economic agencies, data providers, crypto). Each must be verified for access terms before use, and syndicated copies don't count as independent confirmation.

## Notable quotes
> "A research recommendation is a hypothesis, not a guarantee of profit." (§4)

> "A losing trade can be a good decision if it followed a valid process, and a winning trade can be a bad decision if it relied on unjustified risk." (§6)

> "No amount of simulated success should automatically unlock live trading." (§9)

## How it connects
- Defines the planned [[investing-apprentice]] agent and the plan in [[investing-apprentice-plan]].
- Seeds the Investing knowledge section: [[paper-trading]], [[look-ahead-bias]], [[trading-costs]], [[risk-management]], [[promotion-system]] and [[source-reliability]].

## Pages touched by this ingest
- [[investing-apprentice]], [[investing-apprentice-plan]]: created
- [[paper-trading]], [[look-ahead-bias]], [[trading-costs]], [[risk-management]], [[promotion-system]], [[source-reliability]]: created
