# Scheduled Routines

Since 2026-10-11 all four Routines send their job into one long-lived **runner session**,
`session_01KsnWbB84Mq9JRHzKrYk55G` ("Investing Apprentice · runner"). It has this repo checked out,
can push to `claude/practical-galileo-8nwjmp`, and has Gmail. Jobs queue one at a time, so runs
never collide. The first versions (fresh session per run) couldn't reach the repo or Gmail, so they
were deleted.

| Routine | ID | Schedule (Toronto) |
|---|---|---|
| Apprentice · Opportunity scan (every 4 h) | `trig_01QKsnz2SDFE8aPVmfpd7MHK` | 2:13, 6:13, 10:13 AM and PM, daily |
| Apprentice · Pre-market | `trig_01FmUM5ztD9juXXFidRQtDhh` | 8:27 AM Mon–Fri (always emails) |
| Apprentice · After the close | `trig_01U9PAFTabbCKbruyu8eodNT` | 4:33 PM Mon–Fri |
| Apprentice · Hourly experiment | `trig_01AjwVsVAvt7u9R36KUW7PCK` | 10:37 AM–3:37 PM hourly, Mon–Fri |

To see what it did, open the runner session in Claude Code, or check the dashboard.
