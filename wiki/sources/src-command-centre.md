---
type: source
section: brain
title: "Command Centre (agent dashboard) and Investing Apprentice dashboard"
aliases: ["Command Centre", "Apprentice dashboard"]
tags: [agents, dashboard]
created: 2026-10-10
updated: 2026-10-10
sources: [src-command-centre]
raw: app:external/commandcentre
---

# Command Centre and Investing Apprentice dashboard
> **Raw:** two private claude.ai apps owned by Stellan, built in other Claude chats. Agent status is copied into the app database (`external/commandcentre`) on every agent run · **Ingested:** 2026-10-10

## TL;DR
Before this brain existed, Stellan already had an agent **Command Centre** running six agents: Morning Rundown, Inbox Sweep, 6 PM Update, Ace, the FlowPilot n8n workflow, and the Investing Apprentice. The Apprentice has its own dashboard.

## Key points
- **Morning Rundown:** daily 7:45 AM. Sweeps email and every calendar, then lays out the day: clashes, prep, to-dos, and what can wait.
- **Inbox Sweep:** 6 runs a day (8:49 AM to 9:49 PM). Finds dates, deadlines and questions in new email, proposes calendar adds and drafts replies, which Stellan approves in the Command Centre.
- **6 PM Update:** daily around 6 PM. Checks that every agent ran and plans tomorrow.
- **Ace:** on call in Claude chat. Cold outreach for FlowPilot. See [[ace]].
- **FlowPilot workflow:** n8n, runs on each request-page inquiry. Last known run 2026-09-30. The n8n connector has been failing to connect since about 2026-10-10.
- **Investing Apprentice:** weekdays 8:27 AM and 4:33 PM. Researches TSX/US stocks and crypto, makes forecasts and pretend trades with $1,000 CAD of virtual money, and earns promotions up a 5-level ladder. Simulation only: there is no code for real-money trading. Status 2026-10-10: Level 1, with no data, because the network blocks its sources or they need free API keys.
- **Apprentice risk rules** (dashboard Settings): long only, a stop-loss on every trade, limits on position, sector and crypto size, a daily-loss halt, and Stellan's approval for any settings change or promotion.

## How it connects
- ⚠️ **Overlap:** the Command Centre's Morning Rundown (7:45 AM) and this brain's Morning Brief (6:30 AM email) both brief the morning. Status: open. Stellan to decide whether to keep both. See [[daily-run-through]].
- Its Inbox Sweep works on **email**. This brain's Link Sorter works on **links Stellan drops in the app**, so they don't overlap.
- Fills in [[investing-apprentice]] (what the product is) and [[connected-apps]].

## Pages touched by this ingest
- [[investing-apprentice]], [[connected-apps]], [[daily-run-through]], [[overview]]
