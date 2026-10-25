# Agent registry

Every agent in Stellan's system: what it does, where it lives, and whether it has been tested.
Sentinel keeps this current. Last updated 2026-10-25.

## On-demand specialists (`.claude/agents/`, called by Atlas, no schedule)
| Agent | Job | Tools | Model | Can't | Last test |
|---|---|---|---|---|---|
| **Atlas** (`.claude/skills/atlas/`) | Coordinator: routes requests, checks results, one answer | all the session has | session default | spend money; send, schedule or publish without OK | not tested |
| **nova** | Business growth: niches, outreach drafts, proposals, weekly pick | Read, Grep, Glob, WebSearch, WebFetch | sonnet | send email (no Gmail tools) | not tested |
| **forge** | Build and fix automations and scripts, dummy-data tests, rollback | Read, Grep, Glob, Edit, Write, Bash, WebFetch | sonnet | switch anything live | not tested |
| **scout** | Focused research, cost-checked, 3–5 findings | Read, Grep, Glob, WebSearch, WebFetch, Write | sonnet | background or repeated searching | not tested |
| **sage** | School: real instructions first, checked maths and accounting | Read, Grep, Glob, Bash, WebFetch, Drive read | sonnet | invent instructions or deadlines | not tested |
| **tempo** | Calendar plans, clashes, 10-minute gap ideas | Read, Calendar read tools | haiku | create, move or delete events | not tested |
| **echo** | Sales role-play, feedback, word of the day | Read, Grep | sonnet | anything outside coaching | not tested |
| **sentinel** | QA, health checks, improvement proposals | Read, Grep, Glob, Bash, list/get scheduled tasks | sonnet | change anything | not tested |

## Scheduled tasks (claude.ai/code/routines)
| Task | Schedule (Toronto) | Status 2026-10-25 |
|---|---|---|
| Brain · Morning brief | daily 6:18 | on |
| Brain · Inbox agent | every 2 h, 6:53–22:53 | on |
| Morning Rundown (Command Centre) | daily 7:45 | on |
| Inbox Sweep (Command Centre) | 8:49, 10:49, 12:49, 14:49, 19:49, 21:49 | on |
| 6 PM Update (Command Centre) | daily 17:51 | on |
| Apprentice · Pre-market / Opportunity scan / After the close | weekdays 8:27 · every 4 h · weekdays 16:33 | on |
| FlowPilot · Outreach morning / afternoon | was weekdays 9:15 and 13:13 | **off** (delete at claude.ai/code/routines) |
| FlowPilot · Prospector, Replies, Weekly report + 5 OLD copies | — | **deleted** 2026-10-25 |

## Rollback
- FlowPilot agents: the job files are still on branch `claude/zen-dirac-x3vtou` in `agents/flowpilot/`.
  To bring one back, create a scheduled task that downloads `protocol.md`, `SKILL_RECOVERY_AND_MAINTENANCE.md`
  and its job file from that branch and follows them (the old schedules are in the table above).
  The two Outreach tasks can simply be switched back on.
- Specialists: delete or edit the file in `.claude/agents/`. Nothing else depends on them except the Atlas routing table.
