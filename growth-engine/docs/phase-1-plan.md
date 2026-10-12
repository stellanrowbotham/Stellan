# FlowPilot Growth Engine · Phase 1: inspection, architecture, plan

*Written 2026-10-12. Status: Phases 1 and 2 done (see [status](#status-by-phase)).*

## 1. What exists today

| Asset | Where | State (2026-10-12) | Reuse? |
|---|---|---|---|
| **FlowPilot website** | Manus, `flowpilot-rob9iwxx.manus.space` (React/Vite SPA) | Live and polished, with a dark charcoal and warm gold look (`#0b0b0b`, `#d7b873`, `#c9a45d`, DM Sans + Space Grotesk). Offers: Instant Reply from $300, Follow-up system from $600, Custom from $1,000, Care plan $149/month. **The demo form is a stub that never sends** (§3). | **Keep.** It's the conversion surface. Wire its forms to the API (`website/`). |
| **Request page** | WebsitePublisher, `project28751.websitepublisher.ai` | Older "free automation plan" page with navy/blue branding, noindex (free plan). It posts to an n8n cloud webhook. | **Retire** once the site's own form is live. It uses the old positioning and branding. |
| **n8n cloud** | `stellan-row.app.n8n.cloud` | One inquiry workflow (webhook → email Stellan + confirmation). Last known run 2026-09-30. The claude.ai n8n connector fails to connect, so it can't be inspected from here. | **Keep n8n as the orchestrator.** The existing workflow gets replaced by WF-05 after its export is reviewed. |
| **ACE (cold email)** | Claude chats + Google Doc log | 69 businesses emailed 2026-09-13 to 09-15. Replies aren't recorded. Stellan reports **no customers from it**. | **Don't extend.** Its no-repeat log seeds `suppression_list` / `businesses` (do_not_contact for anyone who asked). It isn't a channel to scale. |
| **Stellan's Brain** (this repo) | GitHub `stellanrowbotham/Stellan` (**public**) | Wiki, agents, live app. No application code. | It hosts `growth-engine/` for now. **Recommendation: move it to a private repo** (questions below). |
| **Command Centre, Brain app** | claude.ai artifacts | Agent dashboards for Stellan's personal workflows | Separate from this system. The Growth dashboard is built in Phase 6. |

Nothing existing is replaced in Phases 1–2. The website is untouched until Stellan pastes the Manus prompt.

## 2. What must be built

Everything in the brief is new except the website and n8n: database/CRM, API, Inquiry Check, the seven
agents, nine workflows and the dashboard. Phases 1–2 deliver the foundation everything else writes to.

## 3. Findings that change priorities

1. **The website captures no leads today.** The demo form's submit function (bundle `index-Dei9OAhi.js`)
   is `await sleep(650); return { ok: false, mode: "local" }`. Visitors who try the demo see an error,
   and the only working intake is the off-brand request page. **This is the cheapest, highest-impact fix
   in the whole plan:** deploy the API and paste the Manus prompt.
2. **Pricing is inconsistent on the site:** "from $600" in the hero, meta and FAQ, against "from $300" on the Instant Reply card.
   The conversion assistant may only quote published prices, so this needs one answer.
3. **Unsourced statistics** on the site ("…didn't reply within 5 minutes", "7 times more likely"). The
   brief rules out unsupported claims, so these need citations or removal.
4. **Cold email produced no customers.** The plan leads with inbound (Inquiry Check, useful content,
   search) and referral partners. Outbound exists only as reviewed, consent-checked drafts.

## 4. Architecture

```
 Visitors ──► FlowPilot website (Manus) ──► growth-api ───────────────► Supabase Postgres (schema `growth`)
               forms, Inquiry Check UI      Edge Function or Node        CRM · consent · suppression · evidence
                                            validate · rate-limit ·      · analytics · workflow log
                                            idempotent · CASL copy        ▲    │ event_outbox
                                                                          │    ▼
 n8n (orchestration) ◄────────────────────────────────────────────────────┘  claim → act → complete
   WF-01 discovery · WF-02 research/score · WF-03 audit · WF-04 content · WF-05 intake
   WF-06 qualify/book · WF-07 partners · WF-08 report · WF-09 errors/retention
        │ calls (through n8n credentials, never stored in the repo)
        ├─ LLM API (Claude by default; provider + model are config) → JSON-schema-validated output only
        ├─ Search/Places API (discovery) · page fetcher with SSRF guard (research, audits)
        ├─ Email (transactional provider) · SMS (optional) · scheduling (Cal.com/Calendly/Google)
        └─ Google Analytics 4 / Search Console (reporting)
 Stellan ──► Growth dashboard (Phase 6, Supabase Auth) → approval queue, pipeline, health, spend
```

**Design rules (enforced in the database, so no workflow or agent can skip them):**
- **Send gate:** every outbound email or text is a row in `outbound_messages`. Postgres triggers check
  suppression, the consent basis for the message's purpose, CASL identification and unsubscribe tokens,
  and human approval. They re-check right before sending. Commercial messages always need per-message
  approval by a human owner or operator.
- **Suppression is global and append-only.** Even the service role can't delete it. Only the owner
  can lift an entry, through `remove_suppression()`, and that's audited.
- **Purpose limits use.** A lead's `purpose` (audit report, demo, consultation…) decides which
  messages are allowed. An audit request never creates marketing consent. Tests prove this.
- **Least privilege.** The public API's database user can call exactly three functions and can't read
  any table. n8n gets its own role. Browsers never get database keys.
- **Replaceable providers.** LLM, search, email, SMS and scheduling are chosen by n8n credentials and
  env config. Only the API has code, and it's provider-neutral (web-standard `Request`/`Response`, runs
  on Supabase Edge Functions, Node, or Workers).
- **Mock mode.** `GROWTH_TEST_MODE=true` marks every record `is_test`. The dashboard and reports
  exclude test data by default.

## 5. Data model (Phase 2, built)

`businesses` (deduped by normalized domain, or name + city) · `source_observations` (every fact with URL,
method, verified/inferred, freshness) · `research_reports` · `scoring_models` (versioned 100-point
model, weights must sum to 100) · `lead_scores` (checked against the model) · `referral_partners` ·
`contacts` · `leads` (+ `lead_stage_history`) · `consent_records` (append-only, exact wording) ·
`consent_current` (view) · `suppression_list` (append-only) · `audit_sessions` · `bookings` · `deals` ·
`message_templates` · `outbound_messages` · `content_drafts` · `content_publications` ·
`approval_queue` (view) · `analytics_events` · `workflow_runs` · `workflow_errors` (also the
invalid-AI-output queue) · `ai_usage` · `spending_limits` · `rate_limits` · `event_outbox` ·
`retention_policies` · `audit_log` (append-only) · `app_users`.

## 6. Credentials and accounts needed

| # | What | Needed for | Who creates it | Free tier? |
|---|---|---|---|---|
| 1 | **Supabase project** (Canada Central region `ca-central-1`) | Database, Edge Function, dashboard auth | Stellan signs up, then shares the project ref. Claude needs a **database connection string** or Supabase access to run migrations. | Yes |
| 2 | **n8n**: fix the claude.ai connector, or an n8n API key | Importing and testing WF-01…09, and checking the existing workflow | Stellan (Settings → Connectors, or n8n → Settings → API) | Existing plan |
| 3 | **LLM API key** (Anthropic by default) | Research, classification, drafting (Phases 3–6) | Stellan, stored only in n8n credentials | Pay-as-you-go. Caps are set in `spending_limits` ($3/day, $40/month to start) |
| 4 | **Search/discovery API**: Google Places API (New) *or* Brave Search API | WF-01, WF-07 | Stellan | Both have free monthly credit |
| 5 | **Transactional email**: Resend, Postmark or Brevo, plus a **sending domain** you control | Demo replies, request responses, approved follow-ups | Stellan (DNS: SPF/DKIM/DMARC) | Yes |
| 6 | **Scheduling**: Cal.com (recommended, has a free API) or Calendly | 15-minute inquiry review booking (WF-06) | Stellan | Yes |
| 7 | **Google Analytics 4 + Search Console** access for the site | WF-08 and content attribution | Stellan adds a service account email as viewer | Yes |
| 8 | SMS (Twilio), optional, later | Text alerts to Stellan only at first | Stellan | Paid |

**Not needed:** any password in chat. Secrets go into Supabase secrets and n8n credentials, never into this repo.

## 7. Questions for Stellan

**Blocking the next step (deploy):**
1. Can you create the Supabase project (Canada region) and give me access to run migrations? A
   connection string pasted into the environment's secrets works, or the Supabase connector.
2. Can you reconnect the n8n connector in claude.ai (it fails with a 404 right now), or create an n8n API key?
3. **Repo:** this repo is public. The code holds no secrets or customer data, but do you want a separate
   **private** repo `flowpilot-growth-engine`? (Recommended. I'd move `growth-engine/` there.)

**Business decisions (they set what the assistant may say):**
4. **Floor price:** $300 (Instant Reply card) or $600 (hero/FAQ)? Are the 50%-off "first 5" offer and
   the 14-day fix-or-refund guarantee current?
5. **Mailing address for CASL:** every commercial email must show a physical mailing address (a PO box
   or virtual mailbox is fine). What should it be?
6. **Sending domain:** do you own a domain for FlowPilot email (rather than gmail.com)? Commercial
   email from a Gmail address will have poor deliverability, and providers won't verify it.
7. **Statistics on the site:** do you have sources for the "5 minutes / 40% / 7 times" figures? If not, I'll
   draft replacement copy without numbers.
8. **Service area:** which towns can you serve in person? This sets the scoring model's service-area
   criteria and the discovery searches. ACE's 16 towns are the default.
9. **Booking:** fine with Cal.com for the 15-minute review, and which hours are you available?
10. **Approved consent wording:** the marketing checkbox text in `api/src/consent-copy.ts` is new. OK as written?

## Status by phase

| Phase | Status | Evidence |
|---|---|---|
| 1 Inspect & plan | ✅ Done | This document |
| 2 Database, CRM, lead capture, consent | ✅ Built and tested locally. ⏳ Not deployed (needs Q1) | 8 migrations · 6 SQL test suites · 22 API tests incl. HTTP end-to-end · Edge Function run under Deno |
| 3 Inquiry Check | Next | — |
| 4–7 | Not started | — |

### Definition of done: where Phases 1–2 leave it

| # | Item | Status |
|---|---|---|
| 1 | Prospect discovered, deduplicated, saved | ◑ Dedupe and save are built and tested (`upsert_business`). Discovery comes in Phase 4. |
| 3 | Audit safely captures an optional lead | ◑ Capture path and audit linkage tested. The audit tool comes in Phase 3. |
| 4 | Real website submission reaches the CRM | ◑ Tested end to end over HTTP against local Postgres. **Live needs Supabase + the Manus change.** |
| 5 | Consented follow-up / approved response takes the correct path | ◑ Send gate tested: consent, purpose, suppression, approval, CASL tokens. Sending comes in Phase 5. |
| 8 | Failures alert without duplicate messages | ◑ Idempotency keys, outbox, error dedupe and backoff tested. Alerts come with WF-09. |
| 9 | Secrets and dependencies documented | ✅ §6 above, `api/.env.example`, `docs/setup.md` |
| 2, 6, 7, 10 | Research, booking, funnel metrics, deploy | Later phases |
