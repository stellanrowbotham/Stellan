# Inbox agent (Link Sorter · Stock Agent · Schedule Agent)

Runs every 2 hours from 6:53 to 22:53 Toronto time. The Morning Brief also runs this file first.

1. Do the protocol setup (`agents/protocol.md` §0).
2. `ArtifactData query` on `inbox` for `status == "queued"`, and separately for `status == "working"`
   items older than 3 hours. If there are none: set `agents/router` to idle with
   `lastSummary: "Checked the inbox at <h:mm a> — nothing new."`, log one activity line, and **stop** (no commit).
3. Set `agents/router` to running. Then, for each item, oldest first (at most 8 per run; leave the rest queued):
   1. Set the item to `working`.
   2. **Sort it (Link Sorter).** Use `intent` if it isn't `auto`. Otherwise decide from the note and the link:
      - **schedule:** game or practice schedules, event listings, timetables, "add to my schedule"
      - **stock:** a ticker, a stock or crypto page, "learn about this stock or coin"
      - **apprentice:** product ideas, investing-app competitors, APIs and data for the Apprentice
      - **flowpilot:** automation tools, client sites, leads, business ideas, ACE material
      - **save:** anything else worth keeping
      Write the chosen intent back to the item and give it a short `title`.
   3. Hand the item to the matching handler below.
   4. Set the item to `done` (or `needs_help`) with `result` (2–4 plain sentences of what was done and
      where it lives), `handledAt`, `handledBy`, and `wikiPage`.
4. File everything into the wiki in one pass (protocol §4). Make one commit per item, or one commit for
   the whole run if the items are small.
5. Set each agent you acted as to idle with a `lastSummary` that has counts, e.g. "Sorted 3 links: 1
   schedule, 1 stock, 1 saved."

## Handler: Schedule Agent (`agents/schedule`)
1. Read the link (protocol §3). Pull out every dated event: title, start, end (assume 1 h if missing),
   location, and whether it's all day. Use the times as written. If the page names a time zone, use it;
   otherwise use America/Toronto.
2. Keep only what Stellan asked for. For example, "just the U13 games" means only those games. If
   the request is ambiguous, keep upcoming events only (today onward).
3. For each event, if it isn't already in the calendar, call Google Calendar `create_event` on the
   primary calendar with `timeZone: "America/Toronto"`, a description containing the source URL and the
   line "Added by Stellan's Brain", and default reminders. Store `calendarEventId`.
4. Write each event to `schedule/<YYYYMMDD>-<slug>` with `calendar: true`.
5. Wiki: create or update `wiki/daily/schedule.md` (the upcoming list) and capture the raw text.
6. Result example: "Added 8 games (Oct 12 – Nov 30) to Google Calendar and your brain. Next: Sat Oct 12,
   9:00 AM at Galt Arena." If more than 25 events, add the next 25 and say how many remain.

## Handler: Stock Agent (`agents/stock`)
1. Work out the ticker or coin from the link and note. If it's unclear, set `needs_help` and ask which one.
2. Research with `WebSearch` (2–5 searches, mode standard; use extended only for a deep request) and
   `WebFetch` where it works. Cover: what the company or coin is, how it makes money or its use case, the
   latest dated news, key numbers with dates, bull points, risks, and anything Stellan's note asked.
3. Write or refresh `research/<TICKER>` (merge into existing research, keep sources with dates), and the
   wiki page `wiki/investing/research-<ticker-lowercase>.md` (type `entity`, kind `asset`), linked from
   the [[investing-apprentice]] hub's Research block. Also add a source page per useful article.
4. Never give buy or sell advice. End the summary with what to watch next, for example earnings dates.
5. If Stellan seems to want this for the Apprentice product (for example "how would our app analyze
   this"), add a note under the hub's Open questions or Features.

## Handler: Apprentice / FlowPilot / save
1. Read the link (protocol §3) and capture it raw.
2. Write the source page, and integrate the facts into the right hub and section pages (CLAUDE.md §6.3,
   unsupervised). Client or lead info goes to `client-<name>.md` under `wiki/flowpilot/`.
3. Result: what it is, the 1–3 most useful takeaways, and the page it was filed to.
