---
type: hub
section: flowpilot
title: FlowPilot
aliases: ["FlowPilot Automation", "Flow Pilot"]
tags: [business, ai, automation]
created: 2026-10-10
updated: 2026-10-12
sources: [src-flowpilot-website, src-flowpilot-request-page, src-ace-outreach-log, src-command-centre]
---

# FlowPilot
FlowPilot Automation, Stellan's AI automations business for local small businesses *(Stellan, 2026-10-10)* ([[src-flowpilot-request-page]]).

## Snapshot
- **Offer:** instant inquiry replies for home-service businesses in southwestern Ontario. Setups **start at $300** (decided 2026-10-12): $300 / $600 / $1,000, plus an optional $149/month care plan. ([[src-flowpilot-website]])
- **Website:** the Manus site is live, but **its demo form is a stub and captures no leads**. Its CTA goes to the older request page. ([[src-flowpilot-website]], [[src-flowpilot-request-page]])
- **Growth plan:** the [[growth-engine]] (inbound-first, AI agents + n8n + CRM) started 2026-10-12. Phases 1–2 are built and tested locally and not yet deployed. *(Stellan, 2026-10-12)*
- **Cold outreach:** [[ace]] emailed 69 businesses (2026-09-13 to 09-15) with no customers so far *(Stellan, 2026-10-12)* ([[src-ace-outreach-log]]).
- **Health:** the n8n workflow's last known run was 2026-09-30, and the claude.ai n8n connector is still failing (2026-10-12). ([[src-command-centre]])

## What FlowPilot sells
A simple system that replies to new inquiries instantly, texts the owner the details, keeps one list of inquiries, and reminds them to follow up. It works with the tools the business already uses, and the owner approves every message. ([[src-flowpilot-website]]) The older request page frames it as a free "automation plan" for any small business ([[src-flowpilot-request-page]]).

## Offers & pricing
| Offer | Price | Source |
|---|---|---|
| Instant Reply (one inquiry source, instant reply, alert, list, 30 days support) | from $300 one-time | [[src-flowpilot-website]] |
| Follow-up system (adds reminders and status tracking) | from $600 one-time | [[src-flowpilot-website]] |
| Custom (multiple sources, booking, quote follow-ups, review requests) | from $1,000 one-time | [[src-flowpilot-website]] |
| Care plan (monitoring, fixes, small changes) | $149/month, optional | [[src-flowpilot-website]] |
| Launch offer: first 5 businesses | 50% off setup for an honest review | [[src-flowpilot-website]] |
| Guarantee | fix free or refund setup within 14 days of launch | [[src-flowpilot-website]] |

⚠️ The hero and FAQ say "from $600", but the Instant Reply card says $300 ([[src-flowpilot-website]]). Status: **resolved 2026-10-12, starting price is $300** ([[decision-2026-10-12-floor-price-300]]). The site copy still needs updating.

## Clients & pipeline
| Stage | Count | Notes |
|---|---|---|
| Emailed by ACE | 69 | Real estate, dental, salons, bakeries, fitness, landscaping, pet grooming, auto, accounting, cleaning, restaurants and more, across 16 SW Ontario towns ([[src-ace-outreach-log]]) |
| Replied | *(not captured)* | Stellan handles replies personally |
| Requested a plan | *(not captured)* | Arrives through the n8n workflow |
| Clients | *(not captured)* | |

## Tool stack
- **n8n cloud:** inquiry workflow (webhook, then an email to Stellan and a confirmation to the visitor). ([[src-flowpilot-request-page]])
- **WebsitePublisher:** hosts the request page (free plan). ([[src-flowpilot-request-page]])
- **Manus:** hosts the FlowPilot website *(Stellan, 2026-10-10)*. It's reachable from the cloud environment as of 2026-10-12 ([[src-flowpilot-website]]).
- **[[growth-engine]] (planned):** Supabase Postgres CRM, a lead API (Supabase Edge Function), and n8n workflows WF-01…09 *(synthesis)*.
- **Claude:** [[ace]] for outreach, Gmail for sending.

## Processes
1. **Outreach** ([[ace]]): find local businesses, check the no-repeat log, send one email each, then log the batch. ([[src-ace-outreach-log]])
2. **Intake:** request page, then the n8n workflow emails Stellan and the visitor gets a confirmation email. ([[src-flowpilot-request-page]])
3. **Follow-up:** Stellan answers replies personally. ([[src-ace-outreach-log]])

## Goals & numbers
- Primary conversion goal: a qualified lead or a booked free 15-minute inquiry review. Secondary: referral partnerships *(Stellan, 2026-10-12)*.
- Ideal first customer: small home-service businesses in southwestern Ontario (landscaping, contractors and similar) that get website inquiries or estimate requests *(Stellan, 2026-10-12)*.

## ACE
[[ace]] is FlowPilot's outreach agent. Use **Talk to ACE** in the app to open a new Claude chat already talking to ACE.

## Open questions
1. Have any of the 69 businesses replied or booked a call?
2. Are the 50%-off launch offer and the 14-day guarantee current?
3. What mailing address should go in commercial emails (CASL)? A PO box is fine.
4. Do you have a domain for FlowPilot email, and sources for the site's response-time statistics?
5. Can you create the Supabase project (Canada region) and reconnect the n8n connector so the [[growth-engine]] can be deployed?
6. What's the 90-day goal (clients, revenue)?

## Pages
- [[ace]]: outreach agent
- [[growth-engine]]: the inbound customer acquisition system (Phases 1–2 built)
- Decisions: [[decision-2026-10-12-floor-price-300]]
- Sources: [[src-flowpilot-website]] · [[src-flowpilot-request-page]] · [[src-ace-outreach-log]] · [[src-command-centre]]
- Related: [[connected-apps]] · [[investing-apprentice]] · [[daily-run-through]] · [[overview]]
