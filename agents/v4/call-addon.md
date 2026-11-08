# Call addon: the morning call reads the daily update

Added to the v3 `call.md` for the **morning** call only (routine at 6:41 AM, call arrives ~6:45). Read after `call.md`; where they disagree, this wins.

1. Read `daily/<today>` (written by the Chief of Staff at 6:15). If it is missing or older than 3 hours, say in the script "your plan isn't ready" and carry on with the v3 sections.
2. Build the script from it instead of re-deriving the day: **Your day** = `plan`; then, each only if non-empty and in one or two sentences: Practice, Inbox (how many need an answer, how many drafts are waiting), Follow-ups, Outreach (who replied or was accepted, by type: "a sponsor replied"), Research (best find or an answer to a question he asked), Bookings, Heads-up. On Monday and Friday read the **Weekly review** (≤ 120 extra words).
   Never read email addresses, full names of outreach contacts or message text aloud; use counts and types.
3. Close with: "That's your update. Tell me what you want done, by voice or typing, in the box under the call." The page then offers the two-way box; whatever he says becomes a task for the right agent.
4. Questions: keep the v3 rules, but if `daily.needsAnswer` has items (a booking needing details, a profile to fill in), ask them as `text` questions with `topic: "open"`.
5. Check `messages` where `to == "stellan"` and `status == new`: mention each in one sentence, then set it `done`.
