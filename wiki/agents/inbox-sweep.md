---
type: agent
kind: routine
title: Inbox Sweep
aliases: ["Email sweep"]
tags: [agents, scheduled]
status: live
schedule: 8:49, 10:49, 12:49, 14:49, 19:49, 21:49 Toronto
created: 2026-10-10
updated: 2026-10-10
sources: [src-agent-roster-2026-10-10]
---

# Inbox Sweep
A quick email and calendar check six times a day, so nothing new sits unnoticed for long.

## What it does
- Checks email since its last run for dates, deadlines and questions: games, practices, tee times, school forms, appointments.
- Proposes calendar adds (Stellan approves them in [[stellans-brain]]) and drafts replies in his writing style. It never sends.
- Looks 48 hours ahead on every calendar for new clashes, including events Stellan added himself.
- Patches today's plan only if something changed. It writes no brief.
- Pushes a notification only when something new needs Stellan.

All of the above is from [[src-agent-roster-2026-10-10]].

## Key facts
- Claude Routine `trig_01YJP6jnXvnk1urxghamTfP2`, cron `49 8,10,12,14,19,21 * * *` Toronto time ([[src-agent-roster-2026-10-10]]).
- Status on 2026-10-10 (2:50 PM run): **ok**. "Only a US Kids Golf promo since 12:51 PM and no clashes in the next 48 hours; Sunday's 2:45 PM U16 game vs Sarnia is still clear." ([[src-agent-roster-2026-10-10]])
- There's no sweep at 4:49 PM. The [[six-pm-update]] covers that gap *(synthesis)*.

## Connections
- [[morning-rundown]], [[six-pm-update]]: the bookends of its day
- [[agents-24-7]]
