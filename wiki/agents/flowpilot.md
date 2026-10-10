---
type: agent
kind: workflow
title: FlowPilot
aliases: ["FlowPilot Inquiry Notifications"]
tags: [agents, business, n8n]
status: attention
schedule: event-driven (each website inquiry)
created: 2026-10-10
updated: 2026-10-10
sources: [src-agent-roster-2026-10-10]
---

# FlowPilot
An n8n automation, not a chat AI. When someone submits the FlowPilot request page, it emails Stellan and sends the visitor a confirmation.

## What it does
- Runs instantly on each inquiry, at any hour ([[src-agent-roster-2026-10-10]]).
- n8n workflow name: "FlowPilot Inquiry Notifications" ([[src-agent-roster-2026-10-10]]).

## Key facts
- Status: **attention**. The last confirmed run was 2026-09-30 and it succeeded ([[src-agent-roster-2026-10-10]]).
- ⚠️ The [[six-pm-update]] can't check it because the n8n connector fails to connect. That has happened on 2026-10-09 and again in this session on 2026-10-10. The n8n trial pause was due 2026-10-06, so the workflow may have stopped. **Action for Stellan:** log in to n8n and check that the workflow is active ([[src-agent-roster-2026-10-10]]).

## Connections
- [[ace]]: the outbound side of the same business *(synthesis)*
- [[agents-24-7]]
