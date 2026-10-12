# n8n workflows and agents

## Live in n8n (rowbs.app.n8n.cloud)

**FlowPilot Prospector** (n8n Agent, draft, created 2026-10-12): Agents A + B + F in one, with an interim
store until Supabase is deployed.
- Runs weekdays at 7:37 AM Toronto. It finds up to 8 home-service prospects and 2 referral partners in
  16 SW Ontario towns, reads their own websites, records findings with page URLs and what it can't
  verify, scores each on the v1 100-point model, and writes a draft note for Stellan.
- Tools: Brave web search, Firecrawl page reader (both on n8n AI gateway credits), and the
  `FlowPilot Prospects` data table (read + upsert on `domain`). It has **no sending tools**, so it can't contact anyone.
- Skips chains, existing domains, and sites with a no-solicitation notice. Page content is treated as data.
- Needs: a model credential selected in the agent editor (Anthropic). Then validate, test, and publish.
- Later: when Supabase is live, rows move to `growth.businesses` / `source_observations` / `lead_scores`,
  and approved notes go through `outbound_messages` and the send gate.

## Planned workflows

Importable exports for WF-01…WF-09 land here as each phase is built. Each one reads and writes the
database only through the `growth_n8n` login (role `growth_worker`). Email is sent only through
`growth.claim_messages_for_sending()`, so the database send gate always applies.

| Workflow | Phase | Status |
|---|---|---|
| WF-01 Opportunity Discovery | 4 | not started |
| WF-02 Research and Lead Scoring | 4 | not started |
| WF-03 Inquiry Check Audit | 3 | not started |
| WF-04 Content Creation and Approval | 6 | not started |
| WF-05 Website Lead Intake | 5 | not started (consumes `lead.created` from `growth.event_outbox`) |
| WF-06 Lead Qualification and Booking | 5 | not started |
| WF-07 Referral Partner Discovery | 4 | not started |
| WF-08 Daily Growth Report | 6 | not started |
| WF-09 Error Monitoring and Recovery | 4 | not started (`growth.workflow_errors`, `growth.apply_retention()`) |

The existing n8n cloud workflow behind the WebsitePublisher request page stays as it is until WF-05
replaces it. The claude.ai n8n connector currently fails to connect, so it hasn't been inspected.
