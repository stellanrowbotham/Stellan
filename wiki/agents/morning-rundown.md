---
type: agent
kind: routine
title: Morning Rundown
aliases: ["Morning brief agent"]
tags: [agents, scheduled]
status: live
schedule: daily 7:45 AM Toronto
created: 2026-10-10
updated: 2026-10-10
sources: [src-agent-roster-2026-10-10]
---

# Morning Rundown
Builds today's plan every morning at 7:45 AM and is the only agent that reports on school.

## What it does
1. Reads email since its last run and proposes calendar adds and reply drafts. It never sends anything.
2. Pulls every calendar through the end of tomorrow and spots clashes: overlaps, or under 20 minutes between events at different places.
3. **School check:** tracks Classroom and school-board emails in a school tracker. It never says whether homework was handed in, only "double-check this one".
4. Writes today's plan to [[stellans-brain]]: headline, clashes, prep, to-dos, what can wait, school, and the schedule.
5. Checks which of Stellan's email accounts are flowing into the hub.
6. Sends a morning brief (under 220 words) and one push notification.

All of the above is from [[src-agent-roster-2026-10-10]].

## Key facts
- Claude Routine `trig_012fCeAraAr8e4RfeHz8XygK`, cron `45 7 * * *` Toronto time, created 2026-09-30 ([[src-agent-roster-2026-10-10]]).
- Status on 2026-10-10: **attention**. "Free Saturday with only the U13 family game at 4 PM and no clashes; U16 game Sunday 2:45 PM, DECA approval still open and school isn't connected." ([[src-agent-roster-2026-10-10]])
- Gap: school email isn't reaching the hub yet, so the school section reads "not connected" ([[src-agent-roster-2026-10-10]]).

## Connections
- [[inbox-sweep]]: picks up during the day where this agent leaves off
- [[six-pm-update]]: writes tomorrow's plan, which this agent replaces in the morning
- [[agents-24-7]]: where it sits in the day
