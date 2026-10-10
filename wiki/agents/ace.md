---
type: agent
kind: chat-on-demand
title: Ace
aliases: ["Ace outreach agent"]
tags: [agents, business]
status: idle
schedule: on call (runs when Stellan asks in chat)
created: 2026-10-10
updated: 2026-10-10
sources: [src-agent-roster-2026-10-10]
---

# Ace
Stellan's cold-outreach agent for his AI automation business. It lives in a Claude chat and only works when he asks it to.

## What it does
- Finds and contacts businesses for the AI automation business, and keeps a record in the Google Drive file "Ace — Contacted Businesses Log" ([[src-agent-roster-2026-10-10]]).
- It doesn't run on a schedule, so "what Ace is doing right now" is nothing unless Stellan has a chat open with it *(synthesis)*.
- Replies from businesses to this outreach are never drafted by the other agents. They go to the top of Stellan's to-do list because he answers them himself ([[src-agent-roster-2026-10-10]]).

## Key facts
- Status on [[stellans-brain]]: **idle**. Last activity 2026-09-18 (v8 of the outreach log) ([[src-agent-roster-2026-10-10]]).
- Its instructions live in Claude chat, not in a Routine, so this wiki can't see them yet. Paste them in to have them documented ([[src-agent-roster-2026-10-10]]).

## Connections
- [[six-pm-update]]: checks the outreach log date every evening
- [[flowpilot]]: the inbound side of the same business, handling inquiries from the website *(synthesis)*
- [[agents-24-7]]
