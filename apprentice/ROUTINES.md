# Scheduled Routines

Since 2026-10-17 the Routines send their jobs into a fresh runner session,
`session_01AHWNRutcADNMdhhTcEim89` ("Investing Apprentice · runner (v3)", started after the FRED key fix so it sees every key). It has the repo, push access and Gmail.
Jobs queue one at a time, so runs never collide. The old runner (`session_01KsnWbB84Mq9JRHzKrYk55G`) was
archived because its history had grown very long, which made every job more expensive. Refresh the runner
the same way every week or two.

| Routine | ID | Schedule (Toronto) |
|---|---|---|
| Apprentice · Opportunity scan (every 4 h) | `trig_011jQY8a3jz77SGaem5bVFwK` | 2:13, 6:13, 10:13 AM and PM, daily |
| Apprentice · Pre-market (history + lab + report, always emails) | `trig_01X6H2wX6Hf4daZWNGzg5AAC` | 8:27 AM Mon–Fri |
| Apprentice · After the close | `trig_018VSqmrjJudjSaua95JgFcp` | 4:33 PM Mon–Fri |

The hourly experiment was turned off on 2026-10-17, at Stellan's approval.

New keys or environment settings only reach sessions started after the change, so restart the runner after editing keys.
