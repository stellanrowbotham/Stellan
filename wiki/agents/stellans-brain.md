---
type: agent
kind: dashboard
title: Stellan's Brain (dashboard)
aliases: ["The Brain", "Brain dashboard", "Stellan's Brain"]
tags: [agents, hub]
status: live
schedule: always on (web page)
created: 2026-10-10
updated: 2026-10-10
sources: [src-agent-roster-2026-10-10]
---

# Stellan's Brain (dashboard)
The private web dashboard that every one of Stellan's agents reports to. Open it: [the Brain](https://claude.ai/artifact/WApPYiiN9caKKWxuWacLZN).

## What it does
- A Claude artifact with a shared database. Agents don't talk to each other directly. They write to the Brain, and Stellan reads it on his phone or computer ([[src-agent-roster-2026-10-10]]).
- Shows the agent cards (status, last run, one-line summary), today's plan, approvals waiting for a tap, ready reply drafts, briefs, a 7-day log and account-connection status ([[src-agent-roster-2026-10-10]]).
- Stellan approves or declines proposed calendar events here. Agents only act on approvals he has marked "approved" ([[src-agent-roster-2026-10-10]]).

## Who writes to it
| Agent | Writes |
|---|---|
| [[morning-rundown]] | today's plan, morning brief, school tracker, connection status |
| [[inbox-sweep]] | approvals, drafts, plan patches when a new clash appears |
| [[six-pm-update]] | tomorrow's plan, evening brief, health checks for all agents, including [[ace]] and [[flowpilot]] |
| [[investing-apprentice]] | its agent card and log lines; full detail lives on its own dashboard |

## Not the same as this wiki
The Brain is the live **status board** (what's happening now). This wiki is the long-term **memory** (what the agents are, how they work, and what's been learned) *(synthesis)*. The round-the-clock view is in [[agents-24-7]].

## Related
- [[agents-24-7]]
