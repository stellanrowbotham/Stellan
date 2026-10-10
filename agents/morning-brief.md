# Morning Brief

Runs daily at 6:18 Toronto time, so the email lands before 6:30.

1. Do the protocol setup (`agents/protocol.md` §0). Set `agents/brief` to running.
2. **Clear the inbox first:** follow `agents/inbox-agent.md` steps 2–5 for anything queued.
3. **Gather the brief (Toronto dates):**
   - **Today & next 3 days:** Google Calendar `list_events` across the primary calendar and the
     subscribed calendars (`list_calendars`; include the hockey feeds, skip "Holidays in Canada"
     unless a holiday falls in the window). Merge in `schedule` docs from the app that are not
     already covered.
   - **Open loops:** from `wiki/daily/daily-run-through.md`, plus the "Tomorrow first" item on
     yesterday's daily page, if there is one.
   - **Overnight agent work:** yesterday's and today's `activity` docs since the last brief, as 3–6 bullets.
   - **Research:** any `research` docs updated in the last 24 h, as one line each (ticker, the gist,
     and what to watch). Don't add new price claims here.
   - **Needs you:** inbox items with `status == "needs_help"`.
   - **Question of the day:** one Open question from a hub, rotating through the sections (check
     `briefs` for the last one used).
   - **Focus:** the overview's "This week's focus", if set.
4. **Write the email.** Subject: `🧠 Stellan's Brain — <Weekday, Mon D>: <n> events, <n> to do`.
   - Use an HTML body (`htmlBody`) with a plain-text `body` fallback.
   - Short sections in this order: Today, Coming up, Needs you, Open loops, Agents overnight, Research, Question of the day.
   - Skip empty sections, except Today ("Nothing on the calendar today.").
   - Times are in Toronto time.
   - Add a link to the app: https://claude.ai/artifact/RmkjrydKPNeqMoYjDdNXm5
   - End with: "Reply in Claude with 'morning' to start your check-in."
   - Keep it scannable on a phone: under 300 words, no images, inline styles only.
5. Send it with Gmail `send_message` to `rowbs34@gmail.com` (protocol §2: nobody else).
6. Save the same content to `briefs/<YYYY-MM-DD>` (`headline`, `sections`, `sentAt`, `to`) so the app shows it.
7. Set `agents/brief` to idle with lastSummary "Sent today's breakdown: <n> events, <n> loops,
   <n> need you." Log an activity line. Refresh `brain/snapshot` (protocol §4, last step).
8. Only commit to git if the wiki changed (inbox items filed).
