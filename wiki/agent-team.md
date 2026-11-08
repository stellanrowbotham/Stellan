---
type: hub
section: brain
title: Agent team
aliases: ["Agents v4", "Chief of Staff", "Outreach Agent", "Performance Agent", "Research Brain"]
tags: [agents, architecture, routines]
created: 2026-11-08
updated: 2026-11-08
sources: []
---

# Agent team
Four agents (Chief of Staff, Research Brain, Outreach, Performance) that share one memory, message each other, and report on the Brain web page. They work for Stellan at any hour and interrupt him only for urgent items.

## Snapshot
- **Built 2026-11-08** *(Stellan, 2026-11-08)*: the Brain page gained a team section, daily update, per-agent panels, activity log, bus view, history search and switches. Shared memory and the message bus live in the app database.
- **Safe by default:** outreach is **draft-only**, texts are **off**, and booking is limited to low-cost items until Stellan flips the switches on the page *(synthesis)*.
- **Instruction files:** `agents/v4/` (architecture, shared rules, one file per agent). Full design: `agents/v4/ARCHITECTURE.md`.
- **Always-on means routines:** an hourly Dispatcher handles anything waiting; dedicated routines do the daily plan, inbox sweep, outreach sends and training planning *(general knowledge: routines run at most hourly)*.

## How it fits together
| Agent | Job | Talks to |
|---|---|---|
| Chief of Staff | Daily plan 6:15 AM, inbox and drafts, follow-ups, reminders, Monday and Friday reviews | Gets practice blocks from Performance; hands reminders to the Dispatcher |
| Research Brain | On-demand research, booking, opportunities | Hands sponsorships and programs to Outreach |
| Outreach | Contacts, follow-ups, Notion and Sheets mirrors, reply alerts | Receives from Research; alerts Stellan on sponsor or program replies |
| Performance | Hockey and golf planning, hours log, mental game, meals, tournament prep | Tells the Chief of Staff to block practice time |

## Tensions & contradictions
- ⚠️ The v3 Scheduling agent also placed golf and study blocks. Status: resolved by rule: Performance owns hockey and golf training, Scheduling keeps research-review and study blocks (`agents/v4/shared.md` §1).
- ⚠️ v3 said no agent sends email. Status: resolved: Outreach (and Research for booking requests only) may, inside the rails in `agents/v4/outreach.md` and `research-brain.md`.

## Open questions
1. Which text provider: free IFTTT SMS (100 a month) or paid Twilio?
2. Which contact page should the outreach footer link to for a personal (non-FlowPilot) sender?
3. What is Stellan's real hockey and school schedule (the planner uses defaults until then)?
4. Should the Brain page stay shared "anyone with the link", or become private?

## Pages
- [[overview]] · [[connected-apps]] · [[daily-run-through]] · [[flowpilot]] · [[investing-apprentice]]
