# Brain agent team (v4): architecture

Four agents share one memory (the Brain app database) and talk through a message bus stored in that
same database. The Brain web page is the only interface: it shows everything, lets Stellan ask any
agent a question, and holds the switches that turn risky things (sending, texting, booking) on or off.

```
                         ┌──────────────── Brain web page (claude.ai artifact) ───────────────┐
 Stellan ──ask / talk──▶ │ daily update · plan · inbox · outreach · training · research · log │
        ◀──call / text── └───────────────▲───────────────────────────────┬────────────────────┘
                                         │ live reads                    │ writes (asks, switches)
                    ┌────────────────────┴───────────────────────────────▼─────────────────────┐
                    │  SHARED MEMORY = Brain database (ArtifactData)                           │
                    │  messages (bus) · memory · alerts · reminders · daily · activity · …     │
                    └───▲────────────▲─────────────────▲───────────────────▲───────────────────┘
                        │            │                 │                   │
                 Chief of Staff  Research Brain   Outreach Agent    Performance Agent
                 (cos)           (research)       (outreach)        (performance)
                        ▲            ▲                 ▲                   ▲
                        └── scheduled Routines (claude.ai) wake them; Dispatcher wakes any with mail ──┘
```

## 1. What "always on" means here
Agents are claude.ai **Routines**: a fresh Claude session starts on a schedule, reads its instruction
file from this repo, does its job, writes to the database, and ends. Routines run at most once an hour
per schedule, so "any time" is delivered like this:

| Routine | When (Toronto) | Does |
|---|---|---|
| **Brain · Dispatcher** | hourly, 7:07 AM–10:07 PM | Reads the bus. Handles anything addressed to any agent (on-demand research, bookings, tasks from the call), delivers due reminders, delivers urgent alerts by text, checks Gmail for replies from outreach contacts. Exits in seconds when nothing is waiting. |
| **Chief of Staff · Daily plan** | 6:15 AM daily | Builds `daily/<date>` (the full daily update). Mondays and Fridays it also writes the weekly review. Finishes before the 6:41 AM call is built. |
| **Chief of Staff · Inbox sweep** | every 2 h, 8:23 AM–8:23 PM | Gmail: flag what needs an answer, write reply drafts (never sends), track one-day follow-ups. |
| **Outreach · Send** | weekdays 9:20, 13:20, 16:20 | Contacts people and businesses within the caps in `settings/outreach`, follow-ups included. |
| **Performance · Planner** | 7:40 PM daily | Plans practice blocks into Google Calendar, sweeps for gaps, logs hours, starts tournament prep a week out. |
| Brain · Morning call (existing) | 6:41 AM, arrives ~6:45 | Now also reads `daily/<date>` aloud (see `call-addon.md`). |
| Brain · Research (existing) | 5:47 AM, 12:47, 6:47 PM | Now also hands opportunities to Outreach (see `research-brain.md`). |

The Dispatcher is the only thing that makes the agents feel instant: worst case a request waits an hour.
The page can answer simple things on the spot, and says clearly when an answer is still queued.

## 2. Shared memory (Brain database)
Existing collections (v3) stay as they are: `agents, findings, channels, questions, plans, schedule, vocab, calls,
checkins, settings, usage, activity, research, briefs, inbox`. New in v4:

| Doc | Shape | Writer |
|---|---|---|
| `messages/<id>` **the bus** | `{from, to: cos\|research\|outreach\|performance\|stellan, kind: task\|handoff\|info\|request\|answer, subject, body, payload: {}, priority: normal\|urgent, status: new\|done\|rejected, createdAt, handledAt?, handledBy?, result?, refId?}` | any agent, or the page on Stellan's behalf |
| `memory/<slug>` | `{title, text, tags: [], updatedAt, updatedBy}` long-lived facts every agent may read (goals, preferences, standing decisions) | any agent; Stellan via the page |
| `alerts/<id>` | `{kind: reply\|conflict\|deadline\|reminder\|booking\|other, urgent: bool, title, body, from, createdAt, delivery: {push?, sms?: {status, at, provider}}, ack?}` | any agent |
| `reminders/<id>` | `{text, dueAt, channel: sms\|push\|call, status: pending\|sent\|done, createdBy, createdAt, sentAt?}` | cos, Stellan |
| `daily/<YYYY-MM-DD>` | `{date, headline, sections: [{agent, heading, items: []}], plan: [{start, end, title, agent, kind}], needsAnswer: [], followups: [], review?: {kind: monday\|friday, doneThisWeek: [], nextWeek: []}, createdAt}` (the daily update) | cos |
| `mail/<threadId>` | `{from, subject, snippet, state: needs_answer\|drafted\|waiting\|answered\|ignored, draftLink?, flaggedAt, lastSeenAt, waitingDays}` (no bodies) | cos |
| `contacts/<id>` | `{name, org, kind: business\|sponsor\|program\|student\|athlete, channel: email\|linkedin, email?, linkedin?, source, opportunityId?, status: new\|ready\|contacted\|replied\|accepted\|declined\|stopped\|bounced, followupCount, nextFollowupAt?, lastContactedAt?, notionPageId?, sheetSynced?, notes}` | outreach |
| `opportunities/<id>` | `{title, kind: sponsorship\|program\|business, url, deadline?, why, status: new\|assigned\|contacted\|closed, from: research, createdAt}` | research |
| `bookings/<id>` | `{what, place, whenAt, costCad, tier: low\|high, specific: bool, status: proposed\|needs_info\|booked\|needs_you\|failed\|cancelled, link?, confirmation?, note, createdAt}` | research |
| `practice/<id>` | `{sport: hockey\|golf, focus, start, end, hours, status: planned\|done\|skipped, eventId?, asked: cos?, note}` | performance |
| `tournaments/<id>` | `{name, sport, start, end, location, away: bool, prepStartsAt, prep: {travel: [], gamePlan: [], packing: []}}` | performance |
| `mental/<date>` | `{checkin, preGame?, visualization?, journal?}` | Stellan via page, performance reads |
| `meals/<YYYY-WW>` | `{week, days: [{day, meals: []}], note}` (planning only, no logging) | performance |
| `settings/team` | switches and limits (see §5) | Stellan via page |
| `settings/training` | weekly schedule template, targets, away/home games | Stellan via page |

Privacy: this repo is public. Names, emails, replies, schedules, locations and check-in text live **only**
in the database. Instruction files and the wiki never contain them.

## 3. How agents message each other
1. Writer creates `messages/<id>` with `to`, `kind`, `subject`, `payload`, `status: "new"`.
2. The recipient reads `status == "new" && to == me` at the start of every run (the Dispatcher also does it for all four, each hour).
3. Recipient acts, then sets `status: "done"` (or `"rejected"` with a reason), `handledAt`, `handledBy`, and a one-line `result`.
4. `priority: "urgent"` messages also create an `alerts` doc so Stellan hears about it at once (§4).

Examples that are built and tested: Performance → Chief of Staff `kind: task` "block practice 4:15–5:15" lands in the next `daily` plan;
Research → Outreach `kind: handoff` with an `opportunities/<id>` becomes a `contacts/<id>` row.

## 4. Interrupting Stellan
Urgent means exactly: a **reply from a sponsor or program**, a **schedule conflict**, or an **approaching deadline**
(within 48 h). Everything else waits for the daily update. Delivery order for an urgent alert (`shared.md` §6):
1. SMS to Stellan's own number, if `settings/team.notify.sms.enabled` (provider IFTTT or Twilio, see the credentials checklist).
2. Always also a push notification through the Claude app.
No private detail goes in the text ("A sponsor replied. Open your Brain.").

## 5. Switches and limits (`settings/team`, set from the Brain page)
`paused` (stops everything), `dryRun` (every run is a TEST: plans and writes to the database, sends nothing), `outreach {send_mode: DRAFT_ONLY|SEND, daily_send_limit, per_run_limit, max_followups: 3}`,
`notify {push, sms {enabled, provider, maxPerDay}}`, `booking {autoBookMaxCad, requireSpecificAbove}`,
`calendar {autoAddPractice}`. Everything ships **off or in draft** and Stellan turns it on.

## 6. What is real and what is not (honest limits)
- **Texting** needs a provider. IFTTT SMS is free (100/month in Canada, to Stellan's own phone only). Twilio is paid and needs an account.
- **LinkedIn**: there is no official way to send LinkedIn messages automatically, and automating it breaks LinkedIn's rules and risks the account.
  The Outreach Agent finds people, writes the message and queues it; the page has a one-tap Copy + Open button.
- **Booking**: agents can request reservations and appointments by email or no-payment forms. They cannot enter card details; anything that needs payment becomes `needs_you` with the link.
- **Phone call**: the 6:45 "call" is the Brain page speaking aloud (free). Talking back works by voice or typing on the page. A real phone call needs Twilio + a voice agent (optional upgrade).
- **Instant answers**: Routines cannot be woken instantly; the Dispatcher runs hourly.

## 7. Test results (2026-11-08, against the live database, no connectors attached)
| Check | Result |
|---|---|
| Brain page: 41 UI checks against a fake database (rendering, filters, forms, two-step switches, UTC conversion, phone width) | all pass (`dashboard/team-v4/test/run.js`) |
| Chief of Staff: read a bus task from Performance, put it in the daily plan, surfaced the pending booking and an overdue reminder, told the truth about missing Gmail/Calendar | works |
| Research Brain: on-demand question answered with three dated, sourced options and a clear "not verified" list; expensive unspecific booking left as `needs_info`, nothing booked | works |
| Outreach handoff: example page was a 404, so it created no contact and invented nothing | works |
| Performance: planned 14 days from default hours, kept it provisional, told the Chief of Staff, honest about missing Calendar | works |
| **Defects found and fixed** | agents wrote guessed (future) timestamps; a fire-time "TEST" message arrives *after* the agent has started, so agents ran for real first. Fix: section 0 of `shared.md` (real clock) and the `settings/team.dryRun` switch (read before any write). |
| Not tested (needs connectors/credentials): Gmail drafts and sending, Calendar events, Notion/Sheets mirrors, SMS, LinkedIn, real bookings | see `CHECKLIST.md` |

Test method for the future: turn **Dry run** on from the page, fire the routine, read the database, turn it off.
