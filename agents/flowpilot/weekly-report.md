# Weekly report job (Mondays 8:07 Toronto)

Read [protocol.md](protocol.md) first. Agent id: `report`. This job changes nothing except the report.

1. Set `agents/report` to running. Read every `leads` doc and the last 7 `log/<date>` docs. Leave out
   `kind: "test"` rows.
2. Work out, giving the denominator every time ("3 of 25") and marking anything under 20 as "too few
   to judge":
   - leads found this week and in total
   - first emails sent this week, and follow-ups sent
   - for leads first emailed in the last 28 days: reply rate, positive rate (POSITIVE_INTEREST,
     MEETING_REQUEST or PRICING_QUESTION), bounce rate and unsubscribe rate
   - the same rates broken down by `category` and by town
   - meetings, customers, waiting for Stellan (`NEEDS_REVIEW`), failures
   - average check score, and how many emails needed a rewrite
3. Add up to 3 suggestions for next week, each based on a number above and quoting it. Never suggest
   changing prices or the offer, or raising volume, as something to do automatically. Frame those as
   questions for Stellan.
4. Save `reports/<today>` as `{date, metrics, suggestions, text}`. Email the plain-text report with
   `send_message` to `notify_email` only, subject "FlowPilot weekly report <date range>".
5. Log and set the agent idle.
