---
type: agent
kind: routine
title: 6 PM Update
aliases: ["Evening update", "Evening brief agent"]
tags: [agents, scheduled]
status: live
schedule: daily 5:51 PM Toronto
created: 2026-10-10
updated: 2026-10-10
sources: [src-agent-roster-2026-10-10]
---

# 6 PM Update
The evening check-in. It reviews the day, makes sure every other agent did its job, and plans tomorrow.

## What it does
1. Checks email and approvals. It marks a draft "sent" once Stellan has replied in that thread.
2. **Health check:** reads every agent card on [[stellans-brain]] and flags missed runs or errors. If more than 8 things are waiting on Stellan, it warns that he's getting overloaded and suggests what can slip.
3. Checks the outside agents. It looks at [[flowpilot]] through n8n, and at [[ace]] through the modified date of the Drive file "Ace — Contacted Businesses Log".
4. Writes **tomorrow's** plan, an evening brief (under 200 words) and one push notification.

All of the above is from [[src-agent-roster-2026-10-10]].

## Key facts
- Claude Routine `trig_01UtfBGwEBF4NSRiVGczcUxJ`, cron `51 17 * * *` Toronto time ([[src-agent-roster-2026-10-10]]).
- Status after the 2026-10-09 run: **attention**. "n8n still won't connect so FlowPilot is unchecked." ([[src-agent-roster-2026-10-10]])

## Connections
- The supervisor of the group: the only agent that checks on the others *(synthesis)*
- [[agents-24-7]]
