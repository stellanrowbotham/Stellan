---
type: meta
section: brain
title: Log
tags: [meta]
created: 2026-10-10
---

# Log
Append-only, newest at the bottom. Each entry starts with `## [YYYY-MM-DD] op | subject`.
Last 5 entries: `grep "^## \[" wiki/log.md | tail -5`
The log from the earlier LLM Wiki demo (2026-10-01 to 2026-10-02) is in git history at commit `b76fec2`.

## [2026-10-10] schema | v2: LLM Wiki becomes Stellan's Brain
- Stellan asked to clear the LLM Wiki demo and restructure it into three sections. Answers to clarifying questions: FlowPilot is the business, and ACE is Stellan's business assistant in Claude chats. The Apprentice is a product Stellan is building. The daily run-through is a morning check-in plus an end-of-day review. The old pages should be deleted.
- \- deleted the 15 demo pages (sources, entities, concepts, analyses) and 3 raw files (Karpathy idea file, qmd README, qmd code excerpts)
- ~ `CLAUDE.md` rewritten as v2: sections, `hub` and `daily` page types, morning and evening workflows, investing and business guardrails
- ~ `tools/wiki.py`: new page types, plus support for daily pages that link several raw files
- + [[investing-apprentice]], [[flowpilot]], [[ace]], [[daily-run-through]]
- ~ [[overview]] rewritten as the Stellan's Brain home page; [[index]] regrouped by section
- → The first morning check-in fills in the hubs' Open questions, one at a time

## [2026-10-10] schema | v2.1: live app, agents, and the daily email
- Stellan asked for an app showing the brain, daily emails, live agent activity, and a place to drop links (for example a hockey schedule to add to the calendar, or a stock to research). Answers to clarifying questions: email goes to rowbs34@gmail.com at 6:30 AM Toronto time, agents run every 2 h from 7am to 11pm, and schedule links go into Google Calendar as well as the brain.
- + App published: https://claude.ai/artifact/RmkjrydKPNeqMoYjDdNXm5 (private database, readable and writable only by the owner and editors)
- + `agents/README.md`, `agents/protocol.md`, `agents/inbox-agent.md`, `agents/morning-brief.md`
- + [[schedule]]
- ~ `CLAUDE.md` §0/§2/§3/§4/§6.7/§10, [[overview]], [[daily-run-through]], [[index]]
- ⚠️ The cloud environment blocks most websites (nhl.com, finance.yahoo.com, wikipedia.org tested). Web search works. Until network access is widened, agents fall back to search and mark links they can't open as "Needs you".
- → Routines: Brain · Inbox agent and Brain · Morning brief

## [2026-10-10] ingest | Connected apps: Command Centre, Apprentice dashboard, request page, ACE outreach log
- Read: Command Centre app (its 6 agents from its database), Investing Apprentice dashboard, WebsitePublisher request page (project 28751), and Google Doc "Ace — Contacted Businesses Log (v8)". The FlowPilot Manus site couldn't be opened (DNS blocked from the cloud).
- Mode: unsupervised (Stellan asked to "fill it with information")
- + [[src-command-centre]], [[src-flowpilot-request-page]], [[src-ace-outreach-log]], [[connected-apps]]
- ~ [[ace]] (cold-outreach agent, 69 businesses in 4 batches), [[flowpilot]] (offer, funnel, n8n, pipeline), [[investing-apprentice]] (simulation, 5 levels, Level 1, blocked on data), [[daily-run-through]] (open loops), [[schedule]] (team details removed), [[overview]], [[index]]
- ⚠️ Two morning briefings now exist (6:30 AM here, 7:45 AM Command Centre). Status: open
- ⚠️ The GitHub repo is PUBLIC. Business names and emails were kept out of the wiki (aggregates only); the full list is in the app database at `ace/outreach`, without emails
- → Stellan: make the repo private; decide on one or two briefings; reconnect n8n

## [2026-10-10] schema | v2.2: brain map, Talk to ACE, connected apps
- App v2: an Obsidian-style brain map (canvas graph of sections, 10 agents, apps, wiki pages, ACE's 18 industries, 16 towns and 69 businesses, plus inbox and research). Tapping a dot opens a sheet with live status, links and connections. Added a Talk to ACE button and pinned the app to the sidebar for phone use.
- App database: + `external/commandcentre`, + `ace/outreach`, ~ `brain/snapshot` (filled with real information)
- ~ `agents/protocol.md` (sync the Command Centre every run, sync the ACE log daily, public-repo guardrail), `CLAUDE.md` §7 and §10, `tools/wiki.py` (`raw: app:<path>`)

## [2026-11-17] schema | FlowPilot daily Instagram reels
- + `reels/` (engine, calendar of 30 episodes, brand kit, posted log), `agents/flowpilot-reels.md`
- + [[instagram-reels]]
- ~ [[flowpilot]] (Snapshot, Tool stack, Pages), [[index]], CLAUDE.md (§2 layout, §6.7, changelog v2.3)
- ep00 "The Second Shift" made in chat and posted to Instagram @flowpilot2026: https://www.instagram.com/reel/Df0oPRxnKNr/
- ~ the "FlowPilot daily Instagram post" scheduled task: Canva image at 8:32 → a new code-rendered reel at 7:00 AM Toronto
- → ⚠️ videos are committed to the public repo (~12 MB/day); a cheaper host is an open question

## [2026-11-17] schema | Voices for the daily reels + monetization
- + `reels/engine/voice.py` (ElevenLabs lines mixed with music ducking, plus captions), ep00 `voice.json` + `vo/`
- ~ `agents/flowpilot-reels.md` (step 3b: script, generate, download, mix, captions), `reels/README.md` (voice cast, voice styles), `reels/calendar.md` (voice idea per episode)
- + `reels/out/ep00-second-shift-voiced.mp4`: voiced remake of ep00 (Owner + Pilot)
- + [[reels-monetization]] (query filed back) · ~ [[instagram-reels]], [[flowpilot]] (open question 5), [[index]]
- research: Buffer, Hootsuite and WERSM on 2026 monetization; 2026 lists of AI business ideas
- ⚠️ ElevenLabs account usage couldn't be read (the connector needs extra permissions), so the credit budget is unknown

## [2026-11-17] schema | Reel queue: producer + poster (never miss a post)
- ⚠️ The 2026-11-17 5:41 AM run fired but never posted or pushed anything (it had to clone, design, voice, render and post in one session)
- + ep01-plumber-race (sports commentary) and ep02-salon-midnight (midnight booking skit), both voiced, posted by hand: https://www.instagram.com/reel/Df2nZLWiDyC/ · https://www.instagram.com/reel/Df2nlAUnK7A/
- + `reels/queue.json`, `agents/flowpilot-poster.md`, `reels/engine/lib.js` (shared drawing), `reels/engine/music.py` (shared synth)
- ~ `agents/flowpilot-reels.md` is now the producer (keeps 3 ready, never posts); the poster task runs 6:57 AM with backups at 9:57 and 12:57 and alerts by push
- ~ [[instagram-reels]], CLAUDE.md §6.7 + changelog v2.4, `reels/calendar.md`, `reels/posted.md`

## [2026-11-17] edit | Reel producer run (agent run, 7:37 PM)
- Reconciled `reels/queue.json` with Instagram: no new posts since ep01/ep02
- + ep03-dental-noshow (villain parody "The No-Show", split screen, 104 BPM A minor) and ep04-landscape-kitchen ("Bot Kitchen" cooking-show parody, 116 BPM F major swing), both voiced, both `ready`
- Queue: 2 ready + 1 reserve. Next poster run 2026-11-18 6:57 AM picks ep03

## [2026-11-18] edit | Reel producer run (agent run, 7:37 PM)
- Reconciled the queue: ep03-dental-noshow posted 2026-11-18 at 6:58 AM by the poster (https://www.instagram.com/reel/Df4c5y2lm1x/), the first fully automatic post
- + ep05-bakery-documentary (nature-documentary parody, receipt printer, 80 BPM G major) and ep06-gym-levelup (arcade level-up, chiptune 128 BPM), both voiced, both `ready`
- Queue: 3 ready (ep04, ep05, ep06) + 1 reserve

## [2026-11-21] edit | Reel producer run (agent run, 7:37 PM)
- ⚠️ The 2026-11-19 and 2026-11-20 producer runs stalled on a Composio approval prompt and built nothing. This run skipped the Instagram reconcile (the poster dedupes on its own)
- + ep07-autoshop-kanban (job board that moves itself, poll CTA, 100 BPM E) and ep08-realtor-pov (whispered POV, "without a bot" detour, tape rewind, 84 BPM A minor), both voiced, both `ready`
- ⚠️ The Owner voice (Jacob, `bcXKpJEti28IoAWz1NfD`) failed on all 4 takes; ep07 shows the owner's line as on-screen text
- ~ `agents/flowpilot-reels.md` (skip reconcile if Composio prompts), `reels/README.md` (Owner voice note)

## [2026-11-22] edit | Reel producer run (agent run, 7:37 PM)
- Skipped the Instagram reconcile (per the playbook; Composio prompts in this session)
- + ep09-cleaning-mythfact ("Myth or Fact" game show, Old-School Owner loses, 120 BPM Bb) and ep10-restaurant-terminal (retro green terminal, deadpan computer voice, 96 BPM D minor), both voiced, both `ready`
- Voices used without problems: Ian, Bill, Adam (robotic), Melissa, Brian (Pilot)

## [2026-11-23] edit | Reel producer run (agent run, 7:37 PM)
- Skipped the Instagram reconcile (per the playbook)
- + ep11-groomer-tower ("Waitlist Control Tower": radar town map, Pilot as air-traffic control fills a cancelled 2:00 PM slot, local-pride CTA "MAP", 100 BPM E minor), voiced, `ready`
- + ep12-accountant-truecrime ("The Case of the Missing Receipts": noir true-crime parody narrated by Grav, clock spin through 4 weeks, detective document bot, DM "DOCS", 84 BPM C minor), voiced, `ready`
- Voices used without problems: Brian (Pilot, incl. air-traffic style), Laura, Grav. ElevenLabs hit a concurrency limit briefly and retried by itself
- Queue: ep04–ep12 marked `ready` (several have likely posted; the poster dedupes by caption) + 1 reserve
