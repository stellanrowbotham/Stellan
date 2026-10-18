# FlowPilot Growth Engine

An inbound-first customer acquisition system for **FlowPilot Automation**: AI agents coordinated by
n8n, a Postgres CRM with consent and suppression built into the database, and a public API that
connects the FlowPilot website.

> **Status 2026-10-12:** Phases 1–2 are built and tested locally but **not deployed yet**. See
> [docs/phase-1-plan.md](docs/phase-1-plan.md) for the inspection findings, architecture, required
> credentials and open questions.

| Folder | What |
|---|---|
| `docs/` | [Phase 1 plan](docs/phase-1-plan.md) · [setup, deploy, backups](docs/setup.md) |
| `supabase/migrations/` | Database schema (`growth` schema): CRM, consent, suppression, send gate, content, ops, RLS, roles |
| `supabase/tests/` | SQL test suites (dedupe, scoring, intake/consent, send gate, RLS, ops) |
| `supabase/functions/growth-api/` | Supabase Edge Function adapter for the API |
| `api/` | Public API (lead intake, unsubscribe), TypeScript with no build step, plus tests |
| `website/` | Drop-in `lead-capture.js` and the Manus prompt for wiring up the live site |
| `n8n/` | Workflow exports WF-01…09 (from Phase 3 on) |

## Quick check
```bash
sudo -u postgres growth-engine/scripts/db-local.sh test     # 6 SQL suites
cd growth-engine/api && npm install && npm test              # API unit tests (add DB URLs for end-to-end)
```

## Guarantees enforced by the database (not by prompts)
- No email or text leaves without passing the **send gate**: suppression, purpose-specific consent,
  CASL identification and unsubscribe, and human approval for anything commercial. It's re-checked at send time.
- The **suppression list** and **consent records** are append-only, even for the service role.
- An **audit or demo request never becomes marketing consent.**
- The public API's database user can call three functions and **can't read any table**.
- Content can't be approved with unverified claims, and nothing publishes without a human approver.
