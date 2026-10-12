# n8n workflows and agents

The outreach system that runs in n8n cloud (`rowbs.app.n8n.cloud`) is documented in
[`../docs/outreach-system.md`](../docs/outreach-system.md): the audit, diagram, nodes, setup, prompts,
credentials, tests, operating guide and improvements.

## In this folder

| Path | What |
|---|---|
| `workflows/composer.json` | FlowPilot Composer: research, write, independent AI critique, Gmail draft |
| `workflows/sender-v2.json` | FlowPilot Outreach Sender v2: 10:15 and 13:15, atomic claim, limits, MX, send |
| `workflows/reply-monitor.json` | FlowPilot Reply Monitor: 11-way classification, suppression, reply drafts, alerts |
| `workflows/followups.json` | FlowPilot Follow-ups: sync of hand-sent drafts, up to 2 follow-ups in the thread |
| `workflows/weekly-report.json` | FlowPilot Weekly Report: metrics plus AI suggestions, emailed Mondays |
| `workflows/error-alerts.json` | FlowPilot Error Alerts: Error Trigger → Events log + email |
| `workflows/prospector-agent.json` | FlowPilot Prospector agent: tools and task (instructions omitted) |
| `tests/` | Offline tests for the Follow-ups Code nodes (`npm install && npm test`) |

Exports are from 2026-10-12. Credentials appear only as n8n credential IDs and names.

## State on 2026-10-12

- Sending mode is **SEND** (Stellan, 2026-10-12): the Composer starts Sender v2 right after it approves emails.
- The new workflows are **not published**. Old Sender v1 (`JYLp19AwhhrEpswo`) was unpublished when v2
  replaced it.
- The n8n AI gateway credits are used up, so AI steps fail safely until they're topped up or replaced
  with your own keys.

## Later: Supabase

The planned WF-01…WF-09 workflows (see `../docs/phase-1-plan.md`) talk to the Supabase `growth` schema
through `growth_n8n` and send only through `growth.claim_messages_for_sending()`. Once that database is
deployed, the n8n data tables used above should move into it, so the database send gate applies to
outreach too.
