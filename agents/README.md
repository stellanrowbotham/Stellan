# Stellan's Brain: agents

These files are the standing instructions for the scheduled Claude agents. Each scheduled run
(a claude.ai Routine) starts a fresh session, reads its file here, and follows it exactly. To change how
an agent behaves, edit its file. The next run picks up the change.

| Routine | File | When (America/Toronto) | Agents shown in the app |
|---|---|---|---|
| Brain · Morning brief (`trig_01Qh6PkzGjUGoJgPw8jdTBp8`) | [morning-brief.md](morning-brief.md) | daily 6:18 (email lands ~6:30) | Morning Brief (it also clears the inbox first) |
| Brain · Inbox agent (`trig_01HiS5y3PaTTuJQYh6wUdYPX`) | [inbox-agent.md](inbox-agent.md) | 6:53, 8:53 … 22:53 (every 2 h) | Link Sorter, Stock Agent, Schedule Agent |

Shared rules for every run are in [protocol.md](protocol.md). Read it first.

- **App (live brain):** https://claude.ai/artifact/RmkjrydKPNeqMoYjDdNXm5
- **Repo / branch:** `stellanrowbotham/Stellan` @ `ccr-a52a2301-reivsy`
- **Wiki rules:** `CLAUDE.md` at the repo root (the schema). The agents follow it like any other session.

**Connectors:** both Routines need the **Gmail** and **Google Calendar** connectors attached in
claude.ai → Routines → (routine) → Connectors. Without them, the agents still sort and research links and
update the app, but they can't send the email or add calendar events, and they report that in the app.
