---
type: hub
section: brain
title: Connected apps & agents
aliases: ["Connected apps", "Agents", "Everything connected"]
tags: [apps, agents, links]
created: 2026-10-10
updated: 2026-10-10
sources: [src-command-centre, src-flowpilot-request-page, src-ace-outreach-log]
---

# Connected apps & agents
Every app, site, doc and agent that Stellan's Brain is connected to. The app's **Brain map** draws all of these as a graph. Tap any dot to see what it is and what it's doing.

## Snapshot
- **2 apps of agents:** this brain (4 agents) and the Command Centre (6 agents). Their status is shown together in the app.
- **Talk to ACE:** an orange button in the app that opens a new Claude chat with ACE's briefing ready to send.
- **Phone:** the app is pinned in Stellan's Claude sidebar and works in the Claude mobile app.

## Apps & links
| Name | What it is | Where |
|---|---|---|
| Stellan's Brain (the app) | Brain map, link inbox, live agents, schedule, morning breakdown, sections | [claude.ai artifact](https://claude.ai/artifact/RmkjrydKPNeqMoYjDdNXm5) (private) |
| Command Centre | Agent scoreboard, calendar approvals, drafted replies, game plan, briefs ([[src-command-centre]]) | [claude.ai artifact](https://claude.ai/artifact/WApPYiiN9caKKWxuWacLZN) |
| Investing Apprentice dashboard | Paper-trading simulation: research, trades, learning, promotions ([[src-command-centre]]) | [claude.ai artifact](https://claude.ai/artifact/PHFxL9AAwnp1DRxWzXLMUQ) (private) |
| FlowPilot website | The business site, built on Manus | [flowpilot-rob9iwxx.manus.space](https://flowpilot-rob9iwxx.manus.space) |
| Automation request page | "Get a simple automation plan" intake form ([[src-flowpilot-request-page]]) | [project28751.websitepublisher.ai](https://project28751.websitepublisher.ai/) |
| ACE outreach log | No-repeat log of businesses ACE emailed ([[src-ace-outreach-log]]) | Google Doc (linked in the app) |
| n8n cloud | Runs the FlowPilot inquiry workflow ([[src-flowpilot-request-page]]) | n8n cloud (linked in the app) |

## Agents
| Agent | App | When | Job |
|---|---|---|---|
| Link Sorter | This brain | every 2 h, 6:53 AM–10:53 PM | Sorts links dropped in the app's inbox |
| Stock Agent | This brain | with each inbox run | Researches stocks and crypto you send ([[investing-apprentice]]) |
| Schedule Agent | This brain | with each inbox run | Adds schedules to Google Calendar and [[schedule]] |
| Morning Brief | This brain | daily 6:30 AM | Email breakdown to Stellan |
| Morning Rundown | Command Centre | daily 7:45 AM | Email and calendar sweep, then the day's plan ([[src-command-centre]]) |
| Inbox Sweep | Command Centre | 6× a day | Email: dates, deadlines, drafted replies ([[src-command-centre]]) |
| 6 PM Update | Command Centre | daily ~6 PM | Checks every agent ran, plans tomorrow ([[src-command-centre]]) |
| [[ace]] | Command Centre | on call in chat | Cold outreach for [[flowpilot]] |
| FlowPilot workflow | n8n | each inquiry | Emails Stellan and confirms with the visitor ([[src-flowpilot-request-page]]) |
| Investing Apprentice | Command Centre | weekdays 8:27 AM, 4:33 PM | Research, forecasts, paper trades ([[investing-apprentice]]) |

## Tensions & contradictions
- ⚠️ **Two morning briefings:** this brain's 6:30 AM email and the Command Centre's 7:45 AM Morning Rundown. Status: open. Stellan to decide whether to keep both or merge them.

## Open questions
1. Keep both morning briefings, or merge them?
2. Reconnect the n8n connector so the FlowPilot workflow can be checked again?
3. Allow manus.space (and data sources for the Apprentice) in the cloud environment's network settings?

## Pages
- Related: [[overview]] · [[flowpilot]] · [[ace]] · [[investing-apprentice]] · [[daily-run-through]] · [[schedule]]
