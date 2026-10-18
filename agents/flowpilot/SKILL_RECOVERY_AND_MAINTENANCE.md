# FlowPilot agents: recovery and maintenance

Written 2026-10-18 after the FlowPilot scheduled tasks stopped working. Scheduled runs read the
**Run checklist** section of this file every run. Everything else is for Stellan, or for a Claude
session that's repairing the agents.

This repo is public, so this file holds no business names, emails, replies or lead data.

## Run checklist (every scheduled run reads this)

Work through these steps in order, then follow `protocol.md` and your job file.

1. **Fresh session, nobody watching.** Never ask a question or wait for an answer. If something blocks you,
   record it on the dashboard and finish what you can.
2. **Check your tools before doing anything.**
   - ArtifactData is required. If it doesn't load, retry ToolSearch once. If it's still missing, end
     with the summary "ArtifactData unavailable", because you can't record anything.
   - Gmail is required for outreach, replies and report. Try `select:` with the names given in the
     task prompt. If that fails, search by keyword ("gmail send message"). If Gmail is still missing:
     - send nothing and draft nothing
     - set your agent to `error` with a `lastSummary` that starts "Needs you: Gmail is not connected to this scheduled task"
     - log it and stop
   - Outreach also needs the Agent tool, for the independent critic.
     - If the Agent tool is missing, send nothing.
     - Leads you've written stay unsent: mark them `NEEDS_REVIEW` with `failure_reason` "critic unavailable".
     - Log it and set `lastSummary` to "Needs you: critic (Agent tool) unavailable".
     - Never review your own email in its place.
3. **Mark the start.** Set `agents/<you>` to `running` with `lastRunAt` = now. Always finish by
   setting it to `idle` or `error` with a one-sentence `lastSummary`. If you're about to run out of
   time or context, stop new work and do that first.
4. **Never send twice.**
   - Claim every lead before sending (protocol §4).
   - Before sending a first email, search Gmail `in:sent to:<email>`. If anything is there, don't send.
     Mark the lead `NEEDS_REVIEW` with `failure_reason` "already emailed per Gmail".
   - Never retry a send that errored. Mark it `FAILED`.
5. **Retries.**
   - Reads, ToolSearch, WebFetch, WebSearch and dashboard writes that fail on version: retry up to 2
     times. On a version conflict, re-read first, then retry.
   - Gmail `send_message` gets no retries.
   - If a web page fails, skip that lead with the reason. Don't stop the run.
6. **Safety beats volume.** If a check is unclear, choose the safer status (`SKIPPED` or
   `NEEDS_REVIEW`), not a send. Never change `settings/main`, never delete documents, never edit repo
   files, never commit.
7. **Honest summary.** Report only what actually happened. A run that sent 0 because of a blocker
   says so.

## A. Overview

Four agents run as claude.ai scheduled tasks. Each firing starts a **fresh** Claude Code session,
which checks out branch `claude/zen-dirac-x3vtou` and follows `protocol.md` plus a job file.

| Task | Schedule (Toronto) | Job file | Needs Gmail |
|---|---|---|---|
| FlowPilot · Prospector | weekdays 7:41 | prospector.md | no |
| FlowPilot · Outreach morning | weekdays 9:15 | outreach.md | **yes** |
| FlowPilot · Outreach afternoon | weekdays 13:13 | outreach.md | **yes** |
| FlowPilot · Replies | weekdays 9:29, 11:29, 13:29, 15:29, 17:29 | replies.md | **yes** |
| FlowPilot · Weekly report | Mondays 8:07 | weekly-report.md | **yes** (email to self) |

State lives in the "FlowPilot Outreach" dashboard's database: settings, leads, suppression, agent
status, log and reports. Gmail is the connector signed in as the FlowPilot sending address.

## B. Failure report (2026-10-18)

**Symptom.** From 2026-10-13 to 2026-10-16 the scheduled runs reported success, but no emails went out
on schedule and the dashboard showed gaps. One dashboard log entry from 2026-10-13 says Gmail tools
were not available to the run.

**Root causes (confirmed from the task settings and the dashboard log):**
1. **The tasks were bound to one long-running chat session** (`persist_session: true`) instead of
   starting a fresh session each time.
   - Each firing arrived in that chat as a background notification. That session treats a
     background notification as not authorizing outward actions, such as cold emails, so the
     notifications were reported but not acted on.
   - The bound session also restarted often, losing its connectors, and had used most of its context.
   - A "succeeded" run status only meant the message was delivered to that session, not that the job ran.
2. **No connectors were attached to the tasks** (`mcp_connections` empty), so runs couldn't reach Gmail.

**Contrast.** The Brain tasks that do work (inbox agent, morning brief) start a fresh session per
firing.

## C. Repair record (2026-10-18)

- Created 5 new tasks that **start a fresh session on every firing**, with the same schedules and
  push notifications on.
  - Their prompts now include a setup step and a graceful stop with a "Needs you" status when Gmail
    is missing.
  - They also include hard safety rules, and they point to the Run checklist above.
- Disabled the 5 old bound tasks. They're renamed "… (OLD, disabled 2026-10-18)" and not deleted, so
  they can be restored.
- **Found while testing:** fresh scheduled sessions start with no repo checkout and no `add_repo`
  tool, so the first Replies test couldn't read its instructions. All 5 prompts now download
  `protocol.md`, this file and the job file from `raw.githubusercontent.com` (the repo is public)
  with `curl`, and stop with an error if that fails. The prompts also spell out the log doc format,
  because the first test run wrote log entries under the wrong doc ids.
- Added this file. No job file (`protocol.md`, `prospector.md`, `outreach.md`, `replies.md`,
  `weekly-report.md`) was changed.
- **Not done, because the tool refused it:** attaching the Gmail connector to the new tasks. The
  scheduling tool replied that the connectors option isn't available for this account from a
  session. **Stellan has to do this in the claude.ai scheduled tasks (Routines) settings** (section D).

## D. Setup and startup

1. Open claude.ai → Code → scheduled tasks (Routines).
2. For each of **Outreach morning, Outreach afternoon, Replies, Weekly report**, edit the task and
   add the **Gmail** connector. Prospector doesn't need it.
3. Make sure each task can run without approval prompts. Match the setting the working Brain tasks
   use.
4. Check that the 5 "(OLD, disabled …)" tasks stay disabled. If old and new tasks were both enabled,
   two runs could compete. Claims prevent double sends, but it's wasteful.
5. Dashboard `settings/main`: check that `paused` is false and `send_mode` is what you want. Use
   `DRAFT_ONLY` for a cautious first day.
6. To test right away, use "Run now" on a task (section E).

## E. Testing checklist

A manual "Run now" proves the job works in a fresh session. A scheduled run proves it fires unattended.
Both are needed.

- [ ] **Prospector, Run now.** The dashboard shows `agents/prospector` going running → idle, new
      `leads` with status NEW or SKIPPED, and a log entry.
- [ ] **Replies, Run now, before Gmail is attached.** Expect `agents/replies` = error, "Needs you:
      Gmail is not connected". This proves the graceful failure path.
- [ ] **Replies, Run now, after Gmail is attached.** Expect idle with a reply count. A summary
      email goes only to the FlowPilot address, and only if a reply needs Stellan.
- [ ] **Outreach, first time.** With `send_mode: DRAFT_ONLY`, run it once on a weekday in hours and check
      that Gmail drafts have the exact footer and the dashboard shows `gmail_draft_id`. Then switch to
      `SEND`.
- [ ] **Unattended proof.** After the first weekday schedule (7:41, 9:15, 9:29), check each new task's
      last run in the scheduled-tasks list, and its session transcript. The dashboard
      `agents/*.lastRunAt` must show that morning's time.
- [ ] **No duplicates.** No lead has two sent emails. Check Gmail Sent for repeated recipients.

## F. Troubleshooting

| What you see | Likely cause | Fix |
|---|---|---|
| Run "succeeded" but `agents/*.lastRunAt` didn't change | Task bound to a chat session, or the session failed early | Make sure the task starts a fresh session. Open the run's session and read where it stopped |
| "Needs you: Gmail is not connected" | Connector not attached to the task | Section D step 2 |
| Run stops at a permission prompt | Task permission mode | Section D step 3 |
| "critic unavailable" | Agent tool not given to the session | Check the task's tools. Until fixed, leads wait in NEEDS_REVIEW |
| Lead stuck in SENDING | A run died mid-send | The next outreach run resolves it (protocol §4). Never resend by hand without checking Gmail Sent |
| Many SKIPPED "no MX" or "no email" | Normal filtering | None. That's the CASL checks working |
| "Could not load the job files from GitHub" | Branch `claude/zen-dirac-x3vtou` renamed or deleted, the repo made private, or GitHub down | Restore the branch, or change the URL in all 5 task prompts. If the repo goes private, attach it to each task as a repository source instead |

## G. Recovery and rollback

- **Pause everything fast.** Set `settings/main.paused = true` on the dashboard. Outreach sends
  nothing, and Replies still records stops.
- **Roll back to the old tasks** (not recommended, since they're the broken design): disable the 5 new
  tasks and re-enable the "(OLD …)" ones.
- **Undo this repair entirely:** delete the 5 new tasks and remove this file in a commit. The job files
  are unchanged, so nothing else needs reverting.
- **Recover a FAILED or NEEDS_REVIEW lead:** check Gmail Sent first. Then set its status by hand on the
  dashboard.

## H. Maintenance

- **Daily (1 min):** glance at the dashboard agent cards. Any `error` or "Needs you" summary means action.
- **Weekly:** read the Monday report and check suppression is growing as stops come in.
- **When a connector is re-authorized or changed:** re-check that each Gmail task still lists it.
- **When editing job files:** change the file on `claude/zen-dirac-x3vtou`. Runs read it fresh each
  time, so no task edits are needed. Keep the "Run checklist" heading, because the task prompts
  reference it.
- **Never** commit lead data. The repo is public.
