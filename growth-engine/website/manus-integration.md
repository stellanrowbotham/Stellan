# Connecting the FlowPilot website (Manus) to the Growth Engine

The site at `flowpilot-rob9iwxx.manus.space` is built and hosted in Manus, and its source isn't in a repo
this project can reach. So the change is made in Manus, by pasting the prompt below together with
[`lead-capture.js`](lead-capture.js).

## What's wrong today (found 2026-10-12)

- **The live demo form sends nothing.** In the deployed bundle, its submit function waits 650 ms and
  returns `{ ok: false, mode: "local" }`, so every visitor sees "The demo email couldn't be sent right
  now". No lead is stored and no email goes out.
- **"Book my free inquiry check"** points to the older WebsitePublisher request page
  (`project28751.websitepublisher.ai`). That page has different branding (navy/blue) and pitches a
  "free automation plan", and its form goes to the n8n webhook, which hasn't been checked since 2026-09-30.

## Before you paste

1. Deploy the API (docs/setup.md, steps 1–4) and run `curl <API URL>/health` → `{"ok":true,"db":true}`.
2. Put the API URL into `GROWTH_API_URL` at the top of `lead-capture.js`.
3. Add the site's origin to the API's `ALLOWED_ORIGINS`: `https://flowpilot-rob9iwxx.manus.space`, plus
   the custom domain if there is one.

## Prompt to paste into Manus

> Please connect the website's forms to my lead API. Keep all existing design, copy, colours and layout
> exactly as they are, except where noted below.
>
> 1. Add the attached file `lead-capture.js` to the project (for example `client/src/lib/lead-capture.js`).
> 2. **Demo form:** replace the current demo submit function (it waits 650 ms and returns `ok: false`)
>    with a call to `submitLead({ purpose: 'demo_reply', source: 'demo_form', name, email,
>    consents: { follow_up: <the "Stellan can follow up with me…" checkbox> }, honeypot, startedAt })`.
>    Call `formStartedAt()` when the form first renders. Show the existing success message when it
>    returns `ok: true`. If `errors` come back, show each message under its field (`name`, `email`).
>    Otherwise show `message`.
> 3. **Honeypot:** add a text input named `website_confirm` to every form. Hide it from people with CSS
>    (position it off-screen; don't use `display:none`), add `tabindex="-1"` and `autocomplete="off"`,
>    and pass its value as `honeypot`.
> 4. **Inquiry check form:** change "Book my free inquiry check" so it opens an on-site form instead of
>    the external request page. Fields: name, email, business name, business website (optional),
>    business type (Landscaping, Lawn care, HVAC, Plumbing, Electrical, Roofing, General contractor,
>    Cleaning, Other home service), and "What's your biggest headache with inquiries?" (optional, 600
>    characters). Include the checkbox "Stellan can follow up with me about setting this up for my
>    business." (unticked by default). Submit with `submitLead({ purpose: 'inquiry_review',
>    source: 'website_form', …, consents: { follow_up } })`.
> 5. Under every form, add this privacy line linking to /privacy: "FlowPilot Automation (Stellan
>    Rowbotham, southwestern Ontario) uses these details only to respond to this request. Nothing is
>    sold or shared."
> 6. Checkboxes must never be pre-ticked, and the follow-up checkbox must not be required to submit.
> 7. Don't add any analytics or tracking scripts in this change.
> 8. **Pricing copy:** setups start at $300. Change "Flat pricing from $600" in the hero and the
>    page's meta/OG description to "Flat pricing from $300", and change the FAQ answer "Setups start at
>    $600…" to "Setups start at $300, with an optional care plan at $149/month…". Leave the pricing cards
>    as they are.

## After Manus publishes

- Submit the demo form with your own email and check that a row appears in `growth.leads`
  (Supabase → Table editor, or `select * from growth.leads order by created_at desc limit 5;`).
- Submit once more with the same details within a minute. The API deduplicates retries by
  `submission_id`, so a genuine second submission creates a second lead, and that's expected.
- The demo **reply email** itself is sent by WF-05 once an email provider is connected (Phase 5). Until
  then, the lead is captured and Stellan gets the notification, but no automated reply is sent.

## Things on the current site to fix or confirm (business decisions, not code)

| Where | What it says | Issue |
|---|---|---|
| Hero, meta description, FAQ | "Flat pricing from $600" / "Setups start at $600" | **Decided 2026-10-12: $300.** Fixed by item 8 of the prompt above. |
| Problem section | "…of home-service companies didn't reply to a website inquiry within 5 minutes. 40% still hadn't replied 5 days later." and "nearly 7 times more likely…" | No source is shown. These need a citation on the page, or they should come out. |
| Calculator | "How much are slow replies costing you?" with "% of inquiries lost to slow or missed replies" | It's labelled "not a guarantee", which is good. The default percentage it uses needs a source or should be left blank for the visitor to fill in. |
| Pricing | "first 5 local businesses at 50% off setup, in exchange for an honest review" | Fine as an offer. Reviews must be honest and unconditional (Competition Bureau guidance on incentivized reviews). Is this offer still open, and how many spots are left? |
| Pricing | "fix it free or refund your setup within 14 days" | This is a guarantee, so the conversion assistant will quote it exactly. Confirm it's current. |
| Footer, CASL | — | Commercial emails need a **mailing address**. See the open questions. |
