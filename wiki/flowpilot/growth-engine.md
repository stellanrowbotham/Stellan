---
type: entity
kind: product
section: flowpilot
title: FlowPilot Growth Engine
aliases: ["Growth Engine", "customer acquisition system"]
tags: [flowpilot, acquisition, n8n, supabase, agents]
created: 2026-10-12
updated: 2026-10-12
sources: [src-flowpilot-website, src-flowpilot-request-page, src-ace-outreach-log]
---

# FlowPilot Growth Engine
An inbound-first customer acquisition system for [[flowpilot]]: AI agents coordinated by n8n, a Postgres CRM with consent rules built into the database, and an API that connects the FlowPilot website. Code and docs are in `growth-engine/` in this repo.

## Summary
Stellan asked for it on 2026-10-12 because cold email (see [[ace]]) produced no customers *(Stellan, 2026-10-12)*. The plan leads with **inbound**: a free AI "Inquiry Check" of a business's website, useful content, search visibility and referral partners. Seven agents (discovery, research and scoring, Inquiry Check, content, conversion, partners, analyst) run as nine n8n workflows (WF-01…09). Every outbound message waits in a human approval queue *(Stellan, 2026-10-12)*.

The build has 7 phases. **Phases 1–2 are done** (plan; database, CRM, lead capture, consent) and tested locally, but **not deployed**. Deployment is waiting on accounts (Supabase, a working n8n connection) and a few business decisions *(synthesis)*.

## Key facts
- **First agent (2026-10-12):** FlowPilot Prospector in n8n finds and scores local home-service prospects and referral partners each weekday at 7:37 AM, with evidence and draft notes for Stellan to review. It has no sending tools *(synthesis)*.
- **Biggest finding:** the live site's demo form never sends anything (it's a stub), so the site captures no leads today ([[src-flowpilot-website]]). Connecting it is the first, cheapest fix *(synthesis)*.
- **Database guarantees:** the send gate checks suppression, consent for the message's purpose, the CASL sender block and unsubscribe link, and human approval. The suppression list and consent records can't be edited or deleted. An audit or demo request never becomes marketing consent *(synthesis, tested in `growth-engine/supabase/tests`)*.
- **Tests (2026-10-12):** 6 SQL suites and 22 API tests pass, including an HTTP end-to-end run against a local database *(synthesis)*.
- **n8n outreach system (2026-10-12):** Prospector → Composer (AI research, writer and a separate AI critic that scores six areas, at most 2 rewrites, compliance overrides the score) → Gmail **draft** for Stellan → Sender v2 (10:15 and 13:15, atomic claim, daily cap) only once `send_mode` = SEND. It also has a Reply Monitor (11 reply types, auto-suppression), Follow-ups (4 then 7 business days, max 2, stop on reply), a Weekly Report and Error Alerts. Full write-up: `growth-engine/docs/outreach-system.md` *(synthesis)*.
- **Not running yet:** the new workflows are unpublished and the n8n AI credits are used up, so AI steps fail safely (leads stay NEW) *(synthesis)*.
- **Accounts needed:** Supabase (Canada region), n8n access, an LLM API key, a search API, a transactional email provider with a domain, Cal.com, and GA4/Search Console. The full list is in `growth-engine/docs/phase-1-plan.md` *(synthesis)*.

## Tensions & contradictions
- ⚠️ The site says "from $600" in the hero and FAQ, but the Instant Reply card says "from $300" ([[src-flowpilot-website]]). Stellan's brief says $300 *(Stellan, 2026-10-12)*. Status: resolved 2026-10-12, $300 ([[decision-2026-10-12-floor-price-300]]).
- ⚠️ The site's response-time statistics have no source ([[src-flowpilot-website]]). The brief rules out unsupported claims *(Stellan, 2026-10-12)*. Status: open.
- ⚠️ The [[src-flowpilot-request-page|request page]] uses the old positioning and branding. Recommendation: retire it once the site form is live *(synthesis)*. Status: open.

## Connections
- [[flowpilot]]: the business it serves
- [[ace]]: the cold-email channel it replaces as the main approach; ACE's log seeds the do-not-contact data
- [[src-flowpilot-website]]: the conversion surface
- [[connected-apps]]: where it will appear once deployed

## Timeline
- 2026-10-12: Brief received. Phase 1 (inspection and plan) and Phase 2 (database, CRM, lead API, consent) built and tested locally *(Stellan, 2026-10-12)*.
- 2026-10-12: First agent, **FlowPilot Prospector**, built in n8n as a draft. It does weekday prospecting into a review table and never contacts anyone. It's waiting on a model credential before it can be tested *(synthesis)*.
- 2026-10-12: **Outreach sender live** in n8n. Weekdays 10:15, it sends only emails Stellan has approved, with a domain check, a cap of 10 per run, a CASL footer and no double sends. The test send succeeded *(synthesis)*.
- 2026-10-12: **AI acquisition system built in n8n** (Composer with an independent critic, Sender v2, Reply Monitor, Follow-ups, Weekly Report, Error Alerts). Mode is DRAFT_ONLY. Sender v1 was unpublished. Tested with simulated Gmail and AI, plus offline unit tests; the Reply Monitor and live follow-ups are untested *(synthesis)*.
