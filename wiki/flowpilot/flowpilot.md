---
type: hub
section: flowpilot
title: FlowPilot
aliases: ["FlowPilot Automation", "Flow Pilot"]
tags: [business, ai, automation]
created: 2026-10-10
updated: 2026-10-10
sources: [src-flowpilot-request-page, src-ace-outreach-log, src-command-centre]
---

# FlowPilot
FlowPilot Automation, Stellan's AI automations business for local small businesses *(Stellan, 2026-10-10)* ([[src-flowpilot-request-page]]).

## Snapshot
- **Offer:** "Get a simple automation plan for your business." A business describes one repetitive process and gets a plan for a first automation workflow. ([[src-flowpilot-request-page]])
- **Funnel:** [[ace]] cold-emails local businesses, which can request a plan on the request page, and an n8n workflow emails Stellan and confirms with the visitor. ([[src-ace-outreach-log]], [[src-flowpilot-request-page]])
- **Pipeline:** 69 businesses emailed in 4 batches (2026-09-13 to 09-15). Replies aren't recorded in the brain yet. ([[src-ace-outreach-log]])
- **Health:** the n8n workflow's last known run was 2026-09-30, and the n8n connector has been failing since about 2026-10-10, so the workflow can't be checked. ([[src-command-centre]])

## What FlowPilot sells
A first automation for a repetitive process. The page's examples are responding to inquiries, organizing leads, sending confirmations, and creating reminders. "People remain in control of important decisions. Nothing here guarantees business results." ([[src-flowpilot-request-page]])

## Offers & pricing
| Offer | Price | Source |
|---|---|---|
| Free automation plan (request page) | Free *(synthesis: no price is shown)* | [[src-flowpilot-request-page]] |
| First automation build | *(not captured)* | |

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
- **Manus:** hosts the FlowPilot website *(Stellan, 2026-10-10)*. The agents can't open it from the cloud environment yet.
- **Claude:** [[ace]] for outreach, Gmail for sending.

## Processes
1. **Outreach** ([[ace]]): find local businesses, check the no-repeat log, send one email each, then log the batch. ([[src-ace-outreach-log]])
2. **Intake:** request page, then the n8n workflow emails Stellan and the visitor gets a confirmation email. ([[src-flowpilot-request-page]])
3. **Follow-up:** Stellan answers replies personally. ([[src-ace-outreach-log]])

## Goals & numbers
*(Not captured yet.)*

## ACE
[[ace]] is FlowPilot's outreach agent. Use **Talk to ACE** in the app to open a new Claude chat already talking to ACE.

## Open questions
1. Have any of the 69 businesses replied or booked a call?
2. What do you charge for a first automation build?
3. What's the 90-day goal (clients, revenue)?
4. Should the n8n connector be reconnected in claude.ai Settings → Connectors so the agents can check the workflow again?

## Pages
- [[ace]]: outreach agent
- Sources: [[src-flowpilot-request-page]] · [[src-ace-outreach-log]] · [[src-command-centre]]
- Related: [[connected-apps]] · [[investing-apprentice]] · [[daily-run-through]] · [[overview]]
