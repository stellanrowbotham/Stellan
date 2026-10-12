---
type: analysis
section: flowpilot
title: "Decision: FlowPilot's starting price is $300"
aliases: ["floor price", "starting price"]
tags: [flowpilot, pricing, decision]
created: 2026-10-12
updated: 2026-10-12
sources: [src-flowpilot-website]
question: What is the lowest published price for a FlowPilot setup?
---

# Decision: FlowPilot's starting price is $300
> Decided 2026-10-12 by Stellan · Status: active

## Context
The website showed two floor prices: "from $300" on the Instant Reply pricing card, but "Flat pricing from $600" in the hero and meta description and "Setups start at $600" in the FAQ ([[src-flowpilot-website]]). The [[growth-engine]] agents may quote only published prices, so they need one answer.

## Options considered
1. $300: matches the Instant Reply card and Stellan's growth brief.
2. $600: matches the hero and FAQ, which would mean dropping the Instant Reply tier.

## Decision & why
**$300.** FlowPilot setups start at $300 one-time (Instant Reply). Follow-up systems start at $600, custom systems at $1,000, and the optional care plan is $149/month *(Stellan, 2026-10-12)*.

## Follow-ups
- The website's hero, meta description and FAQ still say $600. The fix is included in the Manus prompt (`growth-engine/website/manus-integration.md`).
- The Prospector agent already quotes "from $300".

## Revisit when
Pricing changes, or the launch offer (50% off for the first 5) ends.
