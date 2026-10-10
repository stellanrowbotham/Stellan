# Scheduled Routines (created 2026-10-10)

| Routine | ID | Schedule (Toronto) | State on 2026-10-10 |
|---|---|---|---|
| Apprentice · Pre-market | `trig_01EBzV8jv969JgHxMPNSrwjt` | 8:27 AM Mon–Fri | on |
| Apprentice · After the close | `trig_01A5A8LVVor9ofNUqa4tYF5z` | 4:33 PM Mon–Fri | on |
| Apprentice · Crypto check | `trig_01EZPKbyn9wamX7f7gvKEtpi` | 12:13, 4:13, 8:13 (AM/PM) daily | **paused** until data sites are allowed |
| Apprentice · Hourly experiment | `trig_01CXcNa8V3PhuiNXPq17hKxY` | 10:37–3:37 hourly Mon–Fri | **paused** until data sites are allowed |

Each firing starts a fresh session, attaches this repo, reads `ROUTINE_GUIDE.md` and runs one job.
Their prompts are visible and editable in claude.ai → Routines.

**Connectors:** these Routines were created from a session that couldn't pass connectors, so they have
**no Gmail**. Until Gmail is added to each one (claude.ai → Routines → edit → connectors), runs work but
can't email. The dashboard, ledger and Brain card still update.
