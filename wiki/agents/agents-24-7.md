---
type: analysis
title: What my agents do, 24/7
aliases: ["Agent timeline", "24/7 view", "Agents around the clock"]
tags: [agents]
question: What are all of Stellan's agents doing around the clock?
created: 2026-10-10
updated: 2026-10-10
sources: [src-agent-roster-2026-10-10, src-stellan-investing-apprentice-brief]
---

# What my agents do, 24/7
> Filed from a query on 2026-10-10. Times are Toronto time. For **live** status, open [[stellans-brain]]. This page shows the *pattern* of a normal day.

## Answer: a normal day
| Time | Agent | What it's doing |
|---|---|---|
| 12:00 AM – 7:45 AM | *(nobody scheduled)* | Quiet. [[flowpilot]] still fires if a website inquiry comes in. |
| **7:45 AM** | [[morning-rundown]] | Overnight email, all calendars, school check, today's plan. Morning brief and push notification. |
| 8:49 AM | [[inbox-sweep]] | New email, 48-hour clash check |
| 10:49 AM | [[inbox-sweep]] | same |
| 12:49 PM | [[inbox-sweep]] | same |
| 2:49 PM | [[inbox-sweep]] | same |
| **5:51 PM** | [[six-pm-update]] | Checks that every agent ran, checks FlowPilot and Ace, plans tomorrow. Evening brief and push notification. |
| 7:49 PM | [[inbox-sweep]] | same |
| 9:49 PM | [[inbox-sweep]] | Last check of the day |
| any time | [[flowpilot]] | Answers each website inquiry instantly |
| when asked | [[ace]] | Business outreach in Claude chat |

All schedule facts are from [[src-agent-roster-2026-10-10]].

**Per day:** 8 scheduled Claude runs (1 rundown + 6 sweeps + 1 update), each about 1–2 minutes long ([[src-agent-roster-2026-10-10]]).

## Planned additions: [[investing-apprentice]]
| Time (proposed) | What it would do |
|---|---|
| 8:27 AM (Mon–Fri) | Pre-market research and email report, before the TSX/NYSE open at 9:30 |
| 4:33 PM (Mon–Fri) | After-close update: score the day's forecasts and paper trades |
| every 4 hours, all week | Crypto check, because crypto never closes |

These times are offset a few minutes from the other agents so their runs don't overlap *(synthesis)*. The 8:30 AM / 4:30 PM / 4-hourly schedule was approved by Stellan on 2026-10-10 *(Stellan, 2026-10-10)*. The brief asks for research "at the frequency I choose" ([[src-stellan-investing-apprentice-brief]]).

## Status on 2026-10-10 (snapshot)
| Agent | Status | Last activity |
|---|---|---|
| [[morning-rundown]] | attention (school not connected, a DECA approval is open) | 2026-10-10 7:45 AM ✓ |
| [[inbox-sweep]] | ok | 2026-10-10 2:49 PM ✓ |
| [[six-pm-update]] | attention (FlowPilot unchecked) | 2026-10-09 5:51 PM ✓ |
| [[ace]] | idle | 2026-09-18 |
| [[flowpilot]] | ⚠️ attention: n8n unreachable | 2026-09-30 |
| [[investing-apprentice]] | planned | n/a |

## Basis
- Pages used: [[stellans-brain]], [[src-agent-roster-2026-10-10]], [[src-stellan-investing-apprentice-brief]]
