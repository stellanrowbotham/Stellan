# What Stellan still needs to do (credentials, permissions, decisions)

Nothing here contains a secret. Never paste a key, password or token into the Brain page, a chat or this repo: connect services through their own sign-in screens.

## A. Required before the agents can do real work
| # | What | Where | Why |
|---|---|---|---|
| 1 | **Attach connectors to each routine.** The API for creating routines cannot attach them in this organization, so a routine with no connectors can only read and write the Brain database (the existing Scheduling agent reports "Google Calendar not connected" for the same reason). | claude.ai → Routines → open the routine → Connectors | Chief of Staff (both): Gmail, Google Calendar. Dispatcher: Gmail, Google Calendar, IFTTT (or Composio for Twilio). Outreach: Gmail, Notion, Composio (Google Sheets). Performance: Google Calendar, Composio (Google Sheets). |
| 2 | **Leave "Dry run" on for the first run of each routine**, check what it wrote on the Brain page, then turn Dry run off. **Turn the routines on**, one at a time, after step 1. They were created **disabled** so they cannot burn usage or act before you are ready. | claude.ai → Routines | Suggested order: Chief of Staff plan → Dispatcher → Performance → Outreach. Outreach stays in draft-only until step 6. |
| 3 | **Fill in "What every agent should know"** (goals + outreach profile) on the Brain page. | Brain page → Switches and limits | Outreach only drafts until the profile exists, and never states a fact that is not in it. |
| 4 | **Send your school/hockey schedule** (paste it in any format). | Brain page → Performance → My schedule | The planner uses default hours until then and says its plans are provisional. |

## B. Text messages (urgent alerts and reminders)
Pick one. Until one is connected, urgent items arrive only as a push notification in the Claude app.
- **IFTTT SMS (free, 100 texts a month in Canada, to your own number only).** Connect SMS: https://ifttt.com/sms/activation/start (verify your mobile). Then add your number and turn on "Text alerts" on the Brain page. 100 a month is about 3 a day: urgent items and reminders share that budget (`notify.sms.maxPerDay`).
- **Twilio (paid, unlimited).** Needs a Twilio account and a Twilio number. Connect Twilio in Composio (Composio → Apps → Twilio) and attach Composio to the Dispatcher. The key stays inside Composio. Somebody who pays the Twilio bill (a parent or guardian, if it is their card) should agree first.

## C. Google Sheets mirror
The Drive connector cannot rewrite Sheet contents, so Sheets goes through **Composio Google Sheets**: connect it at Composio → Apps → Google Sheets (the one-time sign-in link expires after 10 minutes; ask Claude for a fresh one). Sheets already created for you: "Brain · Outreach contacts (mirror)" and "Brain · Training log (mirror)". The Notion tracker "Brain · Outreach Tracker" is already created.

## D. Decisions
1. **LinkedIn.** There is no official way to send LinkedIn messages automatically, and automating it breaks LinkedIn's rules and can get the account banned. The Outreach Agent writes the message and queues it; you tap Copy + Open. If you want to risk a third-party automation tool anyway, that is your call and a separate setup (not recommended).
2. **Outreach footer link.** The footer links to the FlowPilot privacy/business page. Keep it, or give a different contact page.
3. **Outreach limits** (page → Switches): 10 emails a day, 2 follow-ups, drafts only until you turn sending on. Turning sending on means the agent emails real organizations from rowbs34@gmail.com without asking each time. Only organization addresses published for enquiries are used (CASL), never individuals' personal addresses or anyone under 18.
4. **Booking money.** No payment method is connected, and agents never type card details. Under $40 CAD (changeable) the Research Brain books by request or no-payment form; anything paid becomes "needs you" with a link.
5. **Real phone call at 6:45.** Today the "call" is the Brain page speaking aloud (free, two-way by voice or typing). A real ringing phone call needs Twilio + a voice agent (ElevenLabs is connected). Say so if you want that.
6. **Page sharing.** The Brain page is shared "Anyone with the link". Its database is locked to you, so people with the link cannot read your data, but set it to Private from the Share menu (Claude cannot change sharing).
7. **Usage.** All routines on = about 28 runs a day (Dispatcher 16, inbox sweep 7, plan 1, Performance 1, Outreach 3 on weekdays). Most runs end in seconds when nothing is waiting, but you recently cut routines to save usage. A leaner setup: Dispatcher every 2 hours (8 runs), inbox sweep 3 times a day. The "Pause all agents" switch on the page stops them all.
