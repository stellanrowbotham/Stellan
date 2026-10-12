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
- **Biggest finding:** the live site's demo form never sends anything (it's a stub), so the site captures no leads today ([[src-flowpilot-website]]). Connecting it is the first, cheapest fix *(synthesis)*.
- **Database guarantees:** the send gate checks suppression, consent for the message's purpose, the CASL sender block and unsubscribe link, and human approval. The suppression list and consent records can't be edited or deleted. An audit or demo request never becomes marketing consent *(synthesis, tested in `growth-engine/supabase/tests`)*.
- **Tests (2026-10-12):** 6 SQL suites and 22 API tests pass, including an HTTP end-to-end run against a local database *(synthesis)*.
- **Accounts needed:** Supabase (Canada region), n8n access, an LLM API key, a search API, a transactional email provider with a domain, Cal.com, and GA4/Search Console. The full list is in `growth-engine/docs/phase-1-plan.md` *(synthesis)*.

## Tensions & contradictions
- ⚠️ The site says "from $600" in the hero and FAQ, but the Instant Reply card says "from $300" ([[src-flowpilot-website]]). Stellan's brief says $300 *(Stellan, 2026-10-12)*. Status: open.
- ⚠️ The site's response-time statistics have no source ([[src-flowpilot-website]]). The brief rules out unsupported claims *(Stellan, 2026-10-12)*. Status: open.
- ⚠️ The [[src-flowpilot-request-page|request page]] uses the old positioning and branding. Recommendation: retire it once the site form is live *(synthesis)*. Status: open.

## Connections
- [[flowpilot]]: the business it serves
- [[ace]]: the cold-email channel it replaces as the main approach; ACE's log seeds the do-not-contact data
- [[src-flowpilot-website]]: the conversion surface
- [[connected-apps]]: where it will appear once deployed

## Timeline
- 2026-10-12: Brief received. Phase 1 (inspection and plan) and Phase 2 (database, CRM, lead API, consent) built and tested locally *(Stellan, 2026-10-12)*.
