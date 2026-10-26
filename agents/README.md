# Stellan's Brain: agents

These files are the standing instructions for the scheduled Claude agents. Each scheduled run
(a claude.ai Routine) starts a fresh session, reads its file here, and follows it exactly. To change how
an agent behaves, edit its file. The next run picks up the change.

| Routine | File | When (America/Toronto) | Agents shown in the app |
|---|---|---|---|
| Brain · Morning brief (`trig_01Qh6PkzGjUGoJgPw8jdTBp8`) | [morning-brief.md](morning-brief.md) | **off since 2026-10-26** (replaced by the morning call) | Morning Brief |
| Brain · Inbox agent (`trig_01HiS5y3PaTTuJQYh6wUdYPX`) | [inbox-agent.md](inbox-agent.md) | 12:53 and 20:53 (cut from every 2 h on 2026-10-26) | Link Sorter, Stock Agent, Schedule Agent |

Shared rules for every run are in [protocol.md](protocol.md). Read it first.

- **App (live brain):** https://claude.ai/artifact/RmkjrydKPNeqMoYjDdNXm5
- **Repo / branch:** `stellanrowbotham/Stellan` @ `ccr-a52a2301-reivsy`
- **Wiki rules:** `CLAUDE.md` at the repo root (the schema). The agents follow it like any other session.

**Connectors:** both Routines need the **Gmail** and **Google Calendar** connectors attached in
claude.ai → Routines → (routine) → Connectors. Without them, the agents still sort and research links and
update the app, but they can't send the email or add calendar events, and they report that in the app.

## v3 agents (2026-10-26)

Instructions live in [`v3/`](v3/): [shared.md](v3/shared.md) (rules and the app database map) plus one job file each. Each run downloads
`shared.md` and its job file from GitHub (no checkout), so it uses less usage. All four run on Sonnet 5.5 and keep private settings
(city, school and sleep hours) in the app database only.

| Routine | File | When (America/Toronto) | Needs connector |
|---|---|---|---|
| Brain · Research (`trig_01MkcXk54xCXqhiqkbx4R4fi`) | [v3/research.md](v3/research.md) | 5:47 AM, 12:47 PM, 6:47 PM | Firecrawl (YouTube transcripts, search); runs on WebSearch alone without it |
| Brain · Scheduling (`trig_01LLLxKuWbyS9GPPLRkTw8B5`) | [v3/scheduling.md](v3/scheduling.md) | 8:11 PM | Google Calendar (without it, the plan is saved with `added: false`) |
| Brain · Morning call (`trig_01SmqhKBv5AriN8wWpNyMbfF`) | [v3/call.md](v3/call.md) | builds 6:41 AM, arrives ~6:45 | Gmail optional (email link); push works without it |
| Brain · Evening call (`trig_01S3P6w15q2ufu7QufPhtej4`) | [v3/call.md](v3/call.md) | builds 5:56 PM, arrives ~6:00 | Gmail optional |

The routines read these files from branch `claude/ecstatic-bohr-78whd2`. After that branch is merged, point the four prompts at `ccr-a52a2301-reivsy` (update the raw GitHub URL in each routine prompt).
Connectors can only be attached in claude.ai (Routines, then Edit, then Connectors), not from a Claude Code session.
