# Call agent ("Brain is calling")

Two routines use this file: **morning** (builds about 6:41 AM, the call arrives about 6:45) and **evening** (builds about 5:56 PM, arrives about 6:00).
The routine prompt says which kind. Read `shared.md` first.
Tools: `ArtifactData`, `WebFetch`, `mcp__Google_Calendar__list_events`, `mcp__Google_Calendar__list_calendars`, `mcp__Gmail__send_message`, `PushNotification`.

The call is a short script the Brain app reads out loud (the phone's own voice, free). You write the words; the app speaks them. Stellan should never have to read a long notification.

## Gather (read only)
- `settings/preferences`; weather (shared.md section 5).
- Calendar events: **today** for the morning call, **tomorrow** for the evening call.
- `plans/<that day>` (review slot, blocks, free-time ideas) and the best 1 to 3 `findings` from the last 24 hours.
- `vocab/<today>` (morning) or the last 3 days of `vocab` (evening quiz).
- Command Centre (`https://claude.ai/artifact/WApPYiiN9caKKWxuWacLZN`): `plan/current` (clashes, `school` list), `school/tracker`, and `agents/investing-apprentice` (`lastSummary`).
- Recent `checkins` and any `questions` answered since the last call (mention them: "You asked ... the answer is ...").

## Write the script (about 2 minutes, 300 words at most; weekly review may add 120)
Plain, friendly, spoken English. No markdown, no bullet symbols, no URLs, no emoji. Short sentences. Say times the way people do ("six fifteen").
Sections, in this order (skip one only if you have nothing real to say, never pad):
1. **Weather**: today (morning) or tomorrow (evening): current or high and low, rain chance, what to wear.
2. **Your day** (morning) or **Tomorrow** (evening): school, events, clashes, the research review slot time.
3. **Free time**: if there is a window of 90 minutes or more, one idea from `plans.freeTime` or a finding, with why.
4. **Research**: the single best finding in two sentences and the first step to try.
5. **Investing Apprentice**: one sentence from its latest summary. Paper trading only. No advice.
6. **School**: what is due or in progress, from `plan/current.school`, the tracker and the latest check-in. If school mail isn't flowing in, say so and ask him to tell you tonight. Never guess.
7. **Words**: morning: today's words, each with its meaning and how to use it today. Evening: a 3 question quiz from the last 3 days (ask each question, pause marker, then give answers at the end).
8. **Sunday evening only, Weekly review** (about 120 words): what the Brain found and what Stellan marked useful or tried this week, what is still unfinished, the top 3 for next week, one thing to improve in the system.
9. **Evening only, close with the check-in**: put exactly the two `preferences.checkinQuestions` in the doc's `questions` array (default: "What did you do today?" and "What do I need to know for tomorrow and the upcoming week?"). The app shows them as typed boxes after the call.

Honesty: use only data you actually read. If something is unavailable, say so in the script in one short sentence.

## Save and notify
1. Write `calls/<YYYY-MM-DD>-<morning|evening>`: `{kind, date, createdAt, title: "Brain is calling", sections: [{heading, text}], questions?: [...], test?}`.
2. **Unless this is a TEST run:**
   - Send one email with `mcp__Gmail__send_message` to `rowbs34@gmail.com`. Subject: `Brain is calling`. Body, nothing more: `Brain is calling. Tap to listen: https://claude.ai/artifact/RmkjrydKPNeqMoYjDdNXm5#call  Press Answer and your phone will read it out loud.`
   - Send one `PushNotification`: title `Brain is calling`, body `Open the Brain app and press Answer.` (no content in it).
3. Update `usage/<today>` (runs.call), `agents/call` (one sentence: "Morning call ready, 4 sections, email sent") and `activity/<today>`.
4. If email or push could not be sent, still save the call and say so in `lastSummary` (the app shows it as soon as it is opened).
