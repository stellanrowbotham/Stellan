---
type: source
section: flowpilot
title: "FlowPilot Automation website (Manus)"
aliases: ["FlowPilot website", "flowpilot-rob9iwxx.manus.space"]
tags: [flowpilot, website, pricing]
created: 2026-10-12
updated: 2026-10-12
sources: [src-flowpilot-website]
raw: raw/flowpilot/2026-10-12-flowpilot-website.md
---

# FlowPilot Automation website (Manus)
> **Raw:** `raw/flowpilot/2026-10-12-flowpilot-website.md` (copy extracted from the live site's JS bundle) · **Author:** Stellan, built in Manus · **Ingested:** 2026-10-12

## TL;DR
FlowPilot's main site positions it as **instant inquiry replies for home-service businesses in southwestern Ontario**. It lists three setup tiers ($300 / $600 / $1,000) and a $149/month care plan. **Its live demo form is a stub: it never sends anything and always shows an error.** Its main CTA sends people to the older request page.

## Key points
- **Positioning:** "Every new inquiry answered in under a minute, even when you're on a job". It sends an instant reply, a text alert to the owner, one list of inquiries, and follow-up reminders, and "you approve every message".
- **Pricing:** Instant Reply from $300 one-time · a follow-up tier from $600 · Custom from $1,000 · Care plan $149/month (optional). The hero, meta description and FAQ say "from $600".
- **Promises:** a one-page plan within 2 days; live in 7–10 days; 30 days of monitoring free; fix it or refund the setup within 14 days of launch; first 5 businesses get 50% off setup in exchange for an honest review.
- **Demo form:** the submit function waits 650 ms and returns `ok: false`, so no lead is captured.
- **Unsourced statistics:** the problem section quotes response-time figures without a source.
- **Look:** dark charcoal `#0b0b0b`, warm gold `#d7b873` / `#c9a45d`, DM Sans + Space Grotesk.

## Notable quotes
- "Most businesses don't need more software. They need fewer loose ends between a new request and the next step."
- "It never pretends to be you having a conversation."

## How it connects
- ⚠️ **Positioning differs from the [[src-flowpilot-request-page|request page]]**, which offers a free "automation plan" for any small business. The site focuses on home-service inquiry replies. Status: open. The [[growth-engine]] plan recommends retiring the request page.
- ⚠️ **Floor price:** $300 on the pricing card, but "from $600" in the hero and FAQ. Status: open (question on [[flowpilot]]).
- The [[growth-engine]] connects this site's forms to a real lead API.

## Pages touched by this ingest
- [[flowpilot]], [[growth-engine]], [[connected-apps]], [[overview]]
