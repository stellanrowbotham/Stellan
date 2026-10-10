---
type: entity
kind: product
section: flowpilot
title: ACE
aliases: ["Ace", "ACE assistant", "business assistant"]
tags: [assistant, claude, flowpilot, outreach]
created: 2026-10-10
updated: 2026-10-10
sources: [src-ace-outreach-log, src-command-centre, src-flowpilot-request-page]
---

# ACE
Stellan's business assistant for [[flowpilot]]. It runs in Claude chats and handles cold outreach to local small businesses *(Stellan, 2026-10-10)* ([[src-command-centre]]).

## Summary
ACE is an on-call agent: it works when Stellan asks for it in a Claude chat ([[src-command-centre]]). Its main job so far has been **cold email outreach**. It finds local businesses, drafts and sends one email to each, and records every contact in a no-repeat log in Google Docs ([[src-ace-outreach-log]]).

**Talk to ACE:** the app's orange **Talk to ACE** button opens a new Claude chat with ACE's briefing already written. The briefing has ACE read its outreach log, report who was emailed and who replied, and suggest the next batch.

## Key facts
- **Outreach to date:** 69 businesses across 4 batches, sent 2026-09-13 to 2026-09-15. ([[src-ace-outreach-log]])
- **Who:** local service businesses in southwestern Ontario. The biggest groups are real estate (8), dental (6), hair salons (6), and bakeries, fitness, landscaping and pet grooming (5 each). The businesses are in 16 towns. ([[src-ace-outreach-log]])
- **Rule:** one outreach email per business, ever. The log is checked before every batch. ([[src-ace-outreach-log]])
- **Replies** are handled by Stellan personally, not by ACE. ([[src-ace-outreach-log]])
- **Log:** v8, last updated 2026-09-18. It replaces all earlier versions. ([[src-ace-outreach-log]], [[src-command-centre]])
- **Privacy:** the business names and emails live in the Google Doc and the app's private database, not in this public repo.

## Open questions
1. Have any of the 69 replied? ACE can check your Gmail when you Talk to ACE.
2. Is ACE a Claude Project with saved instructions? If so, give me its link and the Talk to ACE button will open that project directly.
3. What does ACE pitch in the email: the free automation plan on the [[src-flowpilot-request-page|request page]]?
4. Does "ACE" stand for something?

## Connections
- [[flowpilot]]: the business ACE works for
- [[src-flowpilot-request-page]]: where ACE's prospects can request a plan
- [[connected-apps]]: ACE's place among the agents
- [[daily-run-through]]: replies and follow-ups go into the end-of-day review

## Timeline
- 2026-09-13: Batch 1 sent (20 businesses). ([[src-ace-outreach-log]])
- 2026-09-14: Batch 2 sent (30). ([[src-ace-outreach-log]])
- 2026-09-15: Batches 3 (8) and 4 (11) sent. ([[src-ace-outreach-log]])
- 2026-09-18: Log updated to v8. ([[src-command-centre]])
