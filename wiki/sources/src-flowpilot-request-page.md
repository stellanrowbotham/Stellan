---
type: source
section: flowpilot
title: "FlowPilot Automation request page"
aliases: ["Get Your Automation Plan", "Request Automation Help"]
tags: [flowpilot, website, n8n]
created: 2026-10-10
updated: 2026-10-10
sources: [src-flowpilot-request-page]
raw: app:websitepublisher-28751-index
---

# FlowPilot Automation request page
> **Raw:** the live page at project28751.websitepublisher.ai (WebsitePublisher project 28751, page version 3, updated 2026-09-23). Read via the WebsitePublisher connector · **Author:** Stellan · **Ingested:** 2026-10-10

## TL;DR
FlowPilot's intake page: "Get a simple automation plan for your business." A small business describes one repetitive process and the form sends it to Stellan's n8n workflow. The workflow emails Stellan and, if the visitor asked for it, sends them a one-time confirmation.

## Key points
- **Pitch:** "Tell us about one repetitive process, such as responding to inquiries, organizing leads, sending confirmations, or creating reminders."
- **Form fields:** name, email, phone (required if they choose calls or texts), business name, business type, the process to improve (up to 600 characters), and preferred contact method. It also asks for consent to a one-time confirmation email and, optionally, to marketing emails.
- **Business types offered:** about 60, grouped as food and drink, home and property services, fitness and wellness, beauty, coaching and education, creative and events, professional services, and retail/other.
- **Plumbing:** the form posts JSON (`eventType: service_interest`, `source: flowpilot-request-page`) to an n8n cloud webhook, with a 10-second timeout. The success message promises a confirmation email when consent is given.
- **Safety copy:** the page asks visitors not to enter passwords, payment, medical, ID or confidential customer data, and notes that "Results depend on the business process… Nothing here guarantees business results."
- **Plan:** WebsitePublisher's free plan, so the page is served noindex and has no sitemap.

## How it connects
- This is the front door of [[flowpilot]]. ACE's cold emails bring prospects here. See [[ace]].
- The n8n workflow behind it is tracked as an agent in the Command Centre. See [[connected-apps]].

## Pages touched by this ingest
- [[flowpilot]], [[connected-apps]]
