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

## [2026-11-08] schema | v2.4: agent team (Chief of Staff, Research Brain, Outreach, Performance)
- Stellan asked for four always-on agents with shared memory, a message bus, text alerts, a 6:45 AM daily update and everything inside the Brain page. Built as v4 on top of the existing v3 Research, Scheduling and Call agents.
- + `agents/v4/` (ARCHITECTURE, shared, chief-of-staff, research-brain, outreach, performance, dispatcher, call-addon), `dashboard/team-v4/` (page patch, build script, Playwright test with a fake database), [[agent-team]]
- ~ app database: + `agents/cos|outreach|performance`, + `settings/team`, + `settings/training`, ~ `agents/research`, ~ `settings/preferences` (`qa.perSectionPerDay` 5 → 20)
- ~ [[connected-apps]], [[overview]], [[index]], `CLAUDE.md` §6.7 and §10, `agents/README.md`
- ⚠️ v3 rules changed: Outreach (and Research, for booking requests only) may send email; Performance owns hockey and golf calendar blocks. Both recorded in `agents/v4/shared.md` §1.
- ⚠️ No texting provider is connected yet, and LinkedIn messages cannot be sent automatically (queued for a one-tap send instead).
- → Stellan: choose the text provider, fill in the outreach profile and schedule on the Brain page, decide on Brain page sharing

## [2026-11-08] edit | Agent team: tests, dry-run switch, checklist
- Tested each agent against the live database with no connectors attached (results in `agents/v4/ARCHITECTURE.md` §7). Found and fixed two defects: guessed timestamps, and TEST instructions arriving after a run had started.
- + `agents/v4/CHECKLIST.md`, `settings/team.dryRun` (on) and a Dry run switch on the Brain page; Notion tracker and two Google Sheets created (ids in `settings/team.sync`, in the database only)
- ~ five routines created **disabled** (Dispatcher, Chief of Staff plan and inbox sweep, Outreach, Performance): the API cannot attach connectors in this organization
- ⚠️ The test runs sent one real push notification ("TEST: a sponsor replied") before the dry-run fix. All test data was deleted afterwards.
- → Stellan: attach connectors, choose a text provider, fill in profile and schedule, then turn routines on (see CHECKLIST)
