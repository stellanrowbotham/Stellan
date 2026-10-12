# n8n workflows

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
