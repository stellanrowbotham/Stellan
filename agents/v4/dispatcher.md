# Dispatcher (hourly)

Runs hourly 7:07 AM-10:07 PM Toronto. It makes the agents feel instant: anything waiting for any of the four agents is handled within the hour.
Also delivers reminders and urgent alerts. **If nothing is waiting, exit in under a minute without writing anything except the agent doc.**
Tools: `ArtifactData`, `PushNotification`, Gmail (read: `search_threads, get_thread`), IFTTT or Composio (SMS), and whatever the handled job needs.

## Checks (cheap reads first; stop early when all are empty)
1. `settings/team` switch check (shared §3).
2. `alerts` where `urgent == true` and `delivery` missing → `deliverAlert` delivery steps (shared §6).
3. `reminders` where `status == pending && dueAt <= now`: send per `channel` (`push`; `sms` through the same cap as alerts; `call` = push "Open the Brain to hear it"), set `sent`, activity `kind: text|push`.
4. Replies: Gmail replies from outreach contacts (`outreach.md` "Replies"). A sponsor or program reply → urgent alert (this is the "text me right away" rule).
5. `messages` where `status == new`, grouped by `to`:
   - `research` → run the on-demand part of `research-brain.md` (questions, bookings, handoffs).
   - `cos` → create reminders, plan tasks (they land in the next daily plan) or answer quick questions from the database.
   - `outreach` → handoffs and tasks per `outreach.md`.
   - `performance` → run `performance.md` section 1 sweep for the affected days.
   - `stellan` → leave for the page (it shows them).
6. `questions` queued (section research) → research-brain.md A. Section `schedule` stays with the v3 Scheduling agent.
7. Anything Stellan said on the Brain page or in the call arrives as a `messages` doc with `from: stellan` (or a reminder / question doc the page created itself). Treat it like any other message to that agent.
Download the job file of an agent only when it has work (`curl` the raw file from the same branch as this file).

## Status
`agents/dispatcher` is not shown as an agent card; log one activity item only if something was handled ("handled 2 messages, 1 reminder").
