# Alexa Wake-up

Runs at Stellan's wake time (see the table in `agents/README.md`). It speaks a short run-down of the
day on Stellan's Echo, right after his Alexa alarm goes off.

**How the morning fits together**
1. **Alexa alarm** (set in the Alexa app, not by this agent) wakes Stellan. His Alexa routine
   "When alarm is dismissed" then plays: "Good morning", weather, and today's calendar.
2. **This agent** fires a couple of minutes later and adds the Brain part: Top priorities, what needs
   him, and the first thing to do. It does not repeat the weather.
3. The **Morning Brief** email (6:30) has the full written version.

## Steps
1. Do the protocol setup (`agents/protocol.md` §0). Set `agents/alexa` to running
   (create the doc if missing: `{order: 5, name: "Alexa Wake-up", role: "Speaks the day's run-down on the Echo", cadence: "daily at wake time"}`).
2. **Gather (Toronto date):**
   - Today's events from Google Calendar (primary + subscribed, same rules as the Morning Brief).
   - Today's `briefs/<YYYY-MM-DD>` doc if the Morning Brief already ran. Reuse it; don't redo work.
   - Open loops from `wiki/daily/daily-run-through.md` and yesterday's "Tomorrow first" item.
   - Inbox items with `status == "needs_help"` (count only).
3. **Write the script** to `/tmp/spoken.txt`. Rules:
   - Spoken English, short sentences, 60–90 seconds (about 150–220 words). No URLs, emojis, or markdown.
   - Times as words Alexa reads well ("9:30 AM"). Toronto time.
   - Order: greeting with weekday and date → how many events and the first one → up to 3 events
     that matter → top 2–3 open loops → "needs you" count → one first task → sign-off
     ("Your full brief is in your email. Say 'morning' in Claude to start your check-in.").
   - **Privacy (protocol §2):** the text goes through Voice Monkey and Amazon. Say event titles only, no
     locations, attendees, phone numbers or addresses. No client or business names, no money figures,
     no check-in answers, no stock prices. Say "a client call", "a FlowPilot follow-up".
   - If the calendar can't be read, say so in one line and carry on with the rest.
4. **Speak it:** `python3 tools/alexa.py announce --file /tmp/spoken.txt --chime wake`.
   If `VOICEMONKEY_TOKEN` or `ALEXA_DEVICE` is missing, or the call fails, don't retry beyond the
   script's own retries: set `agents/alexa` to `error` with the exact message and what Stellan can do.
5. Save the script to the `briefs/<YYYY-MM-DD>` doc as `spoken` and `spokenAt` (merge; keep other fields).
6. Set `agents/alexa` to idle with lastSummary "Spoke today's run-down: <n> events, <n> loops."
   Log one activity line. No git commit unless the wiki changed (it normally doesn't).
