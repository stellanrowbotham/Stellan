# FlowPilot outreach system in n8n

*Written 2026-10-12. This covers the AI-powered customer acquisition system built in n8n cloud
(`rowbs.app.n8n.cloud`, Stellan's personal project), as asked for in the "Build My AI-Powered Customer
Acquisition System in n8n" brief.*

**Current state in one line:** every piece is built. Only the old sender (now unpublished) and the
Prospector agent were ever published. Nothing new runs on a schedule until Stellan publishes it.
Sending mode is **DRAFT_ONLY**, so AI-approved emails become Gmail drafts and nothing goes to a
prospect automatically. **AI steps are blocked right now** because the n8n AI gateway credits are used
up ("Payment required").

Contents: [1 Audit](#1-audit-of-the-original-sender) · [2 Diagram](#2-before-and-after) ·
[3 Nodes](#3-workflows-and-their-nodes) · [4 JSON](#4-workflow-json) · [5 Setup](#5-configuration-steps) ·
[6 Prompts](#6-ai-prompts) · [7 Credentials](#7-credentials-and-settings) ·
[8 Tests](#8-test-plan-and-results) · [9 Operating guide](#9-operating-guide) ·
[10 Improvements](#10-prioritised-improvements)

---

## 1. Audit of the original sender

**FlowPilot Outreach Sender v1** (`JYLp19AwhhrEpswo`) was published on 2026-10-12 and **unpublished the
same day** when v2 replaced it. As built, it:

- ran weekdays at 10:15 Toronto, plus "Run now"
- read the `FlowPilot Prospects` table and sent rows Stellan had set to `approved`, up to 10 per run
- checked the address syntax, that the address came from the business's own site, the no-solicitation
  flag, "never sent before", that an email was written, and duplicates within the run
- looked up the domain's mail server (MX) through dns.google
- marked the row `sending` before the Gmail send, then `sent`, `send_failed` or `skipped`
- added the footer (name, business, email, website, business-information link, "reply stop")
- passed one real test send to Stellan

**Gaps against the brief:**

| # | Gap | Risk | Fixed in |
|---|---|---|---|
| 1 | Only a 10:15 window | Slow reply cycle | Sender v2: 10:15 and 13:15, one shared queue |
| 2 | The `sending` mark wasn't conditional | Two overlapping runs could both send | v2 claims with "update where id AND status = APPROVED", plus a run token |
| 3 | No daily limit across runs (only 10 per run) | Volume creep and deliverability damage | `daily_send_limit` and `batch_size_per_window` settings |
| 4 | No spacing between sends | Bursty sending | `spacing_seconds` wait |
| 5 | The email was written and approved by the same agent | No independent quality or compliance check | Composer: separate AI critic (different model) plus deterministic checks |
| 6 | Sent directly | No human look before the first sends | `send_mode` = DRAFT_ONLY (default) or SEND |
| 7 | Any MX failure counted as a bad address | A DNS outage would skip good leads | Transient DNS errors release the lead; only a confirmed missing domain or MX skips it |
| 8 | No suppression list | Someone who said "stop" could be re-added later | `FlowPilot Suppression` table, checked by every workflow |
| 9 | No reply handling | Replies and unsubscribes depended on Stellan noticing | Reply Monitor (11 categories) |
| 10 | No follow-ups | Spec asks for up to 2 | Follow-ups workflow |
| 11 | No event log, no error alerts, no pause or dry-run switch | Silent failures | `FlowPilot Events`, Error Alerts workflow, `paused` and `dry_run` settings |
| 12 | Lowercase, free-form statuses | Inconsistent reporting | Uppercase status set in `FlowPilot Leads` |
| 13 | Retrying after an unclear Gmail result could double-send | Duplicate emails | No retry on send; an unclear result becomes FAILED and is never retried automatically |

## 2. Before and after

```
BEFORE (v1)
 Prospector agent ──► FlowPilot Prospects ──(Stellan sets "approved")──► Sender v1 (10:15) ──► Gmail send
   (finds, scores,      (one table)                                       MX check, footer
    writes email)

AFTER
                          ┌──────────────── FlowPilot Settings (switches) ───────────────┐
                          │          FlowPilot Suppression · FlowPilot Events (log)      │
 Prospector agent ──► FlowPilot Leads (status NEW)                                       │
  (finds + scores)        │                                                              │
                          ▼                                                              │
 Composer (hourly 9:05–16:05 weekdays)                                                   │
   pre-checks → MX → AI research → AI writer → AI critic (≤2 rewrites) → checks          │
   → Gmail DRAFT to the prospect (footer added) → NEEDS_REVIEW                           │
                          │                                                              │
        Stellan reviews the draft in Gmail                                               │
        ├─ DRAFT_ONLY: he sends it himself ──► Follow-ups "sync" spots it ──► SENT       │
        └─ SEND mode: sets APPROVED ──► Sender v2 (10:15, 13:15): claim → MX → send      │
                          │                                     → SENT, draft removed    │
                          ▼                                                              │
 Reply Monitor (Gmail, every 5 min) → AI classify (11 types) → status, suppression,      │
   reply draft in thread (never sent), alert email to Stellan                            │
                          │                                                              │
 Follow-ups (9:35, 14:35 weekdays): thread check → AI writer → AI critic → checks        │
   → Gmail draft in the same thread (or send in SEND mode when approved)                 │
                          │                                                              │
 Weekly Report (Mon 8:05): metrics + ≤3 AI suggestions → email to Stellan (no changes)   │
 Error Alerts: any failed run → Events log + email to Stellan ───────────────────────────┘
```

## 3. Workflows and their nodes

| Workflow | n8n ID | State | Trigger |
|---|---|---|---|
| FlowPilot Composer | `FUaEHVgdSbbhx4qi` | unpublished | weekdays hourly 9:05–16:05, Run now |
| FlowPilot Outreach Sender v2 | `ewY30DPW3LnvGdNz` | unpublished | weekdays 10:15 and 13:15, Run now |
| FlowPilot Reply Monitor | `7GV4Yg4PmPCDUiL9` | unpublished | Gmail poll every 5 min |
| FlowPilot Follow-ups | `9bcTu0RP9gFzn7L4` | unpublished | weekdays 9:35 and 14:35, Run now |
| FlowPilot Weekly Report | `W5esUrCwTzfPD3Nt` | unpublished | Mondays 8:05, Run now |
| FlowPilot Error Alerts | `Xdtu5d7x3xYPvg98` | unpublished | Error Trigger |
| FlowPilot Prospector (Agent) | `C44fxWJme0UbuNe1` | published (old version); draft updated | weekdays 9:37 |
| Outreach Sender v1 | `JYLp19AwhhrEpswo` | **unpublished 2026-10-12** | (was 10:15) |

All times are America/Toronto.

**Composer** (51 nodes): triggers → load Settings, Leads, Suppression → pre-check (status NEW, a valid
public email from the business's own site, not suppressed, no no-solicitation notice, not a duplicate,
contact basis) → loop, one lead at a time → MX lookup → **AI research** (Gemini, JSON: facts with their
URLs, confidence) → research check (confidence ≥ `min_research_confidence`) → **AI writer** (Gemini) →
**AI critic 1** (OpenAI gpt-5-mini, separate model, JSON scores, issues, flags, decision, revision) →
gate (deterministic checks) → critic 2 and 3 when a rewrite is needed (at most 2 rewrites) → finalize →
**Gmail draft** to the prospect with the compliance footer → lead set to NEEDS_REVIEW with the original,
critique, revision, six scores, model and decision → log to Events. Leads that fail checks go to
NEEDS_REVIEW with `ai_decision` = HUMAN_REVIEW and a reason. If AI is unavailable, the lead stays NEW
with `failure_reason` and is retried on the next run.

**Sender v2**: triggers → load → **plan**: rows stuck in SENDING for 15+ minutes go to review; it halts
when paused, `send_mode` ≠ SEND, outside weekdays 8:00–18:00, or the bounce threshold is reached;
room = min(per-window batch, daily limit − sent today − in flight); per-row checks (required fields,
syntax, already contacted, duplicate, same address twice in the batch, suppression, no-solicitation,
contact basis, `ai_decision` APPROVE or HUMAN_APPROVED, final content checks) → loop → **claim**
(update where id AND status = APPROVED → SENDING with `claim_token` = run id) → claimed? → MX
(confirmed bad → SKIPPED; DNS error → release to APPROVED) → dry run? → **Gmail send** (no retry, error
output) → **mark sent** (where id AND SENDING AND token; Gmail ids; first follow-up 4 business days
later at 9:30) → log → delete the review draft → wait `spacing_seconds` → next. A Gmail error → FAILED
(never retried).

**Reply Monitor** (23 nodes): Gmail trigger (`in:inbox -from:me newer_than:3d`) → load Settings, Leads,
processed-reply events → match by Gmail thread (bounce fallback by address) → loop → **AI classify**
(OpenAI; the reply is treated as untrusted) into POSITIVE_INTEREST, MEETING_REQUEST, PRICING_QUESTION,
SERVICE_QUESTION, NOT_NOW, REFERRAL, NOT_INTERESTED, UNSUBSCRIBE, OUT_OF_OFFICE, BOUNCED, UNCLEAR → decide
(a regex forces UNSUBSCRIBE for "stop / remove me / unsubscribe"; a status never moves backwards except
for suppression and bounces) → update the lead (stops follow-ups; out-of-office pushes them 7 days) →
suppress UNSUBSCRIBE, NOT_INTERESTED and BOUNCED → **reply draft** in the thread for positive and
question replies (Gemini, never sent) → alert email to Stellan → log classification and the processed
message id (prevents double handling). If AI fails → UNCLEAR plus an alert.

**Follow-ups** (38 nodes): triggers → load → **plan**: (a) *sync*: leads in NEEDS_REVIEW with a draft,
or APPROVED, are checked for a message Stellan sent by hand (`in:sent to:<email> after:<lead created>`);
if found → SENT, with follow-up 1 due 4 business days later. (b) *due follow-ups*: SENT, no reply, not
suppressed, under `max_followups`, due now, at most `followup_batch` (default 2) per run → loop →
**claim** (conditional on the previous `claim_token`; the due date moves to the next business day first,
so a crash only delays) → **read the Gmail thread**: any inbound message stops follow-ups → AI writer
(Gemini) → **AI critic** (OpenAI) → gate (score ≥ `min_quality_score`, no compliance flags, no factual
issues, 25–150 words, no links, no guarantee or pressure wording) → route:
- DRAFT_ONLY, or anything not approved → **Gmail draft in the same thread**
- SEND and approved → **send in the thread** via the Gmail API (threading headers set)
- dry run → nothing saved
- AI unavailable → retry the next business day

Follow-up 2 is due 7 business days after follow-up 1; after the last one, the due date is cleared.

**Weekly Report** (12 nodes): Monday → load Leads and Events → metrics (test rows excluded; rates use
leads first emailed in the last 28 days as the denominator; anything under 20 is marked "too few to
judge"; split by industry and campaign; failures this week) → up to 3 AI suggestions (Gemini, from the
numbers only, never "send more" or "change the offer") → email to Stellan → log.

**Error Alerts**: Error Trigger → log to Events → email Stellan with the workflow, node and error.

**Prospector agent (draft)**: now writes to `FlowPilot Leads` with status NEW and `email_source_url`
(insert only, so it can't reset an existing lead). The `save_email` tool and the `write_outreach_email`
skill are removed, because the Composer writes the emails now. `set_status` only allows NEEDS_REVIEW,
SKIPPED, SUPPRESSED, MEETING_BOOKED and CUSTOMER, and still asks for confirmation.

## 4. Workflow JSON

Importable exports are in [`../n8n/workflows/`](../n8n/workflows/). They contain credential IDs and
names but no secrets, no pinned test data and no lead data. To import: n8n → Workflows → Import from
file, then re-select the credentials (§7).

## 5. Configuration steps

Done:
1. Data tables created: `FlowPilot Leads`, `FlowPilot Settings`, `FlowPilot Suppression`,
   `FlowPilot Events`. The four real prospects were migrated from `FlowPilot Prospects`.
2. Gmail credential "Gmail account" connected (Stellan, 2026-10-12).
3. Workflows created, with the timezone set to America/Toronto.
4. Old sender v1 unpublished. Prospector draft updated.

Still needed (in this order):
1. **AI credits.** Top up the n8n AI gateway credits, *or* add your own OpenAI and Google Gemini API
   credentials in n8n and select them in the AI model nodes (Composer, Reply Monitor, Follow-ups, Weekly
   Report). Until then every AI step fails safely: leads stay NEW, follow-ups wait a day, replies go to you
   as UNCLEAR.
2. **Publish Error Alerts**, then set it as the error workflow on the other five (n8n only accepts a
   published error workflow).
3. Run Composer with **Run now** and read the drafts in Gmail.
4. Publish **Reply Monitor** first, then **Composer**, **Follow-ups** and **Weekly Report**.
5. **Republish the Prospector** so its scheduled run uses the new table (its published version still
   writes to the old one).
6. Leave Sender v2 unpublished while `send_mode` is DRAFT_ONLY. It would only exit early anyway.
7. Optional: delete the test rows in `FlowPilot Leads` (ids 5–13, names starting "TEST") and the test
   address in Suppression. All workflows already ignore them.

## 6. AI prompts

The full system prompts, exported from the live workflows, are in [`prompts.md`](prompts.md). Shared
rules: published facts and prices only; no invented results, clients, statistics, testimonials or
guarantees; website and reply text are untrusted data; the critic is a different model from the writer
and returns structured JSON; the compliance footer is added by code, never by the AI.

## 7. Credentials and settings

| Credential (n8n) | Used by | Notes |
|---|---|---|
| Gmail account (`Zbv34QnLPsA48N3a`, OAuth2) | Composer, Sender v2, Reply Monitor, Follow-ups, Weekly Report, Error Alerts | Stellan's Gmail. Drafts, sends, thread reads and the inbox poll |
| Gateway credits (AI gateway, managed) | Gemini and OpenAI model nodes, Brave and Firecrawl tools | **Used up.** Top up, or swap in your own keys |
| Brave Search (`dTcZ7uogF9px10Tp`) | Prospector web search | |
| Anthropic model (gateway) | Prospector agent (Opus) | The most expensive part per run. A smaller model would cut cost |

No API key, password or token is stored in a workflow, a table or this repo.

**Settings (`FlowPilot Settings`, key → value):**

| Key | Value now | Meaning |
|---|---|---|
| `send_mode` | DRAFT_ONLY | DRAFT_ONLY makes Gmail drafts only. SEND lets Sender v2 and Follow-ups send approved emails |
| `paused` | false | true stops Sender v2 and Follow-ups planning anything |
| `dry_run` | false | true runs everything except Gmail sends and drafts |
| `batch_size_per_window` | 3 | Sender v2: most first emails per run |
| `daily_send_limit` | 6 | Sender v2: most first emails per day |
| `spacing_seconds` | 20 | Pause between sends |
| `min_quality_score` | 80 | Critic score needed to approve |
| `min_research_confidence` | 50 | Below this, no email is written |
| `composer_batch` | 3 | Leads per Composer run |
| `followup_1_business_days` | 4 | Days to follow-up 1 |
| `followup_2_business_days` | 7 | Days from follow-up 1 to follow-up 2 |
| `max_followups` | 2 | |
| `followup_batch` | *(not set; default 2)* | Follow-ups per run. Add the row to change it |
| `campaign_id` | FP-2026-10-home-services-v1 | Stamped on leads and events |
| `bounce_pause_threshold` | 2 | Sender v2 stops for the day after this many bounces |
| `owner_email` | Stellan's Gmail | Alerts and reports go here |
| `booking_link` | (empty) | Used in reply drafts when set |

## 8. Test plan and results

✅ = performed with the result shown. ⏳ = still required. "Pinned" means Gmail, DNS or AI responses were
simulated in an n8n test run while the data tables were real. "Offline" means the Code-node logic ran
under Node.js with mocked n8n inputs.

| # | Test | Status | Evidence / what's left |
|---|---|---|---|
| 1 | Approved lead is sent once and marked SENT with Gmail ids and a run token | ✅ pinned | Sender v2 test, case A |
| 2 | Duplicate / already-contacted lead is not sent | ✅ pinned | Case B |
| 3 | Invalid address syntax is skipped | ✅ pinned | Case C |
| 4 | Suppressed address is skipped | ✅ pinned | Case D. Follow-ups: offline (email and domain) |
| 5 | Email with unsupported claims is blocked by the final checks | ✅ pinned | Case E. Follow-up gate: offline ("guarantee", links, placeholders) |
| 6 | Row stuck in SENDING goes to review, not resent | ✅ pinned | Case F |
| 7 | Lead without AI approval or without a contact basis is not sent | ✅ pinned | Cases G and H |
| 8 | Two runs racing for the same lead: only one sends | ✅ pinned | Forced resend of a SENT row: the claim matched nothing, Gmail never ran, logged `not_claimed` |
| 9 | Paused, outside hours, weekend: nothing happens | ✅ offline (Follow-ups) · ⏳ Sender v2 live | |
| 10 | Real MX lookups (good domains) | ✅ live | Composer run: both roofers' domains passed |
| 11 | Missing domain (NXDOMAIN) → SKIPPED; DNS outage → lead released | ⏳ | Needs a test row; adding one was declined, so ask first |
| 12 | Gmail send error or unclear result → FAILED, never retried | ⏳ | Needs a forced Gmail error |
| 13 | AI critic rejects and rewrites a weak draft | ✅ live (partly) | Critic 1 scored one real draft 72 with factual issues and wrote a revision. Then credits ran out, so a full pass to APPROVE and a saved draft weren't seen |
| 14 | AI unavailable → no email, lead kept, reason recorded | ✅ live | "Payment required" during research and critic 2: leads stayed NEW with `failure_reason` |
| 15 | Compliance flag overrides a high score | ✅ offline (Follow-ups gate) · ⏳ Composer live | |
| 16 | Reply classified, status updated, unsubscribe suppressed, follow-ups stopped, Stellan alerted | ⏳ | Reply Monitor is untested. Needs AI credits, then a reply to a test email from another address |
| 17 | Follow-up timing (4 then 7 business days), max 2, cancel on reply | ✅ offline (32 checks) · ⏳ live | Live run 2026-10-12 found nothing due and changed nothing |
| 18 | Follow-up sent inside the same thread to the right address | ✅ offline (headers and body checked) · ⏳ live | The SEND path uses `Buffer` in a Code node, not yet run on n8n cloud |
| 19 | Weekly report metrics and email | ✅ live (email pinned) | Real tables. AI suggestions not seen (credits) |
| 20 | Error workflow fires and alerts | ⏳ | It has to be published first |
| 21 | Schedules fire at the right Toronto times | ⏳ | Only after publishing. Check the n8n executions list on the first day |
| 22 | No test failure produced a real email to a prospect | ✅ | Every send and draft in tests was pinned. The only real email went to Stellan (v1 test) |

## 9. Operating guide

**Every weekday (about 10 minutes):**
1. Open Gmail **Drafts**. Each Composer draft is addressed to the prospect, with the footer already
   in place. Read it, edit it if needed, and **send it yourself**, or delete it. If you delete one, set that
   lead to SKIPPED (ask the Prospector, or edit the table).
   Leads the AI couldn't approve (NEEDS_REVIEW with `ai_decision` HUMAN_REVIEW) get **no** Gmail draft.
   Their reason, critique and text are in the `FlowPilot Leads` row. Fix the text and send it yourself,
   or set the lead to SKIPPED.
2. Follow-up drafts appear in the same thread after 4 and then 7 more business days. Send or delete them
   the same way.
3. Reply alerts arrive as "[FlowPilot lead] CATEGORY - Business". Positive and question replies have a
   reply draft waiting in the thread. Nothing is sent for you.
4. Unsubscribes, "not interested" and bounces are suppressed automatically. Never email a suppressed
   address by hand.

**Monday:** read the weekly report. Its suggestions are only suggestions.

**Switches** (edit the value in `FlowPilot Settings`):
- Stop everything now: `paused` = true
- Rehearse without Gmail: `dry_run` = true
- Let the system send approved emails itself: `send_mode` = SEND. Only do this after at least ~20 drafts
  you'd have sent unchanged. Then publish Sender v2. Keep `daily_send_limit` low (Gmail accounts
  sending cold email can be flagged; a separate domain is safer).

**If something breaks:** check `FlowPilot Events` (every step logs there) and the n8n executions list.
A lead's `failure_reason` says why it stopped. FAILED sends are never retried automatically: check Gmail
Sent before resending by hand.

**CASL in practice:** contact only businesses whose email is printed on their own website with no "no
solicitation" notice (implied consent for a conspicuously published address). Every email identifies
Stellan and FlowPilot, links the business-information page that holds the mailing address, and offers
"reply stop". Honour a stop immediately. The Reply Monitor does this when it's running.

## 10. Prioritised improvements

1. **Restore AI** (credits or own keys). Nothing intelligent runs without it.
2. **Publish Error Alerts, then Reply Monitor**, so replies and unsubscribes are caught from the first
   send.
3. **A sending domain** (for example `@flowpilot…`) with SPF, DKIM and DMARC, instead of a personal Gmail.
4. **Run the remaining ⏳ tests** (§8), each with a test lead on an address Stellan controls (with
   his OK).
5. **Cheaper Prospector model** (Sonnet or Haiku class) to cut the per-run cost.
6. **Move the tables to the Supabase growth database** once it's deployed, so the database-level send
   gate (`growth.claim_messages_for_sending`) applies to outreach too.
7. **Better reply matching** for replies that start a new thread (match by sender domain too).
8. **A/B subject lines** once the 28-day sample is over ~40 sends per industry.
