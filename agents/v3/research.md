# Research agent

Runs three times a day (about 5:47 AM, 12:47 PM, 6:47 PM Toronto). Finds the **top 3 new things** worth Stellan's attention,
reads videos, follows good channels, answers his research questions, and (evening run) prepares tomorrow's 5 vocabulary words.
Read `shared.md` first. Tools: `ArtifactData`, `WebSearch`, `WebFetch`, `mcp__Firecrawl__firecrawl_search`, `mcp__Firecrawl__firecrawl_scrape`.

## Steps
1. **Setup and stop checks.** Load tools. Read `settings/preferences`. If `paused` is true, set `agents/research` to `idle`
   ("Paused: low on usage") and stop. Read `usage/<today>`; if Firecrawl credits are at the daily cap, use only WebSearch/WebFetch.
   Set `agents/research` to running.
2. **Pick the slot** from the Toronto time: `am` (before 9:00), `noon` (11:00 to 15:00), `pm` (after 15:00). Topics for the slot:
   - `am`: **business** and **investing**
   - `noon`: **study** and a fresh angle on **business**; also look at followed channels for new videos
   - `pm`: **golf** and **vocab**
3. **Steer.** Read the last 14 days of `findings` (titles and URLs, so you never repeat one) and any `review` ratings: do more of what
   Stellan marked `useful` or `tried`, less of `not_for_me`. Read `channels` (status `following`).
   Read `settings/focus` if it exists (Stellan's answers from the Sunday/Monday check-in). If `researchLookFor` is set, make at least one of
   the 3 findings in every run match it, and let `weekPlan` shape the rest (for example a study method for a test he named). Also read the
   newest `checkins` for anything he asked to learn more about.
4. **Search.** Use `WebSearch` first. Use `firecrawl_search` (`sources: ["web"]`, `domainTools: false`, `limit: 5`, always fill `objective`) for
   YouTube results and anything WebSearch missed. Budget per run: at most 2 Firecrawl searches and 2 video reads.
   What each topic means:
   - **business:** small-business ideas Stellan can build *inside Claude* (skills, scheduled tasks, connectors, Claude Code) and sell
     through FlowPilot. For each: the owner's problem, what gets built, free or cheap tools, rough build time, how to test with dummy data.
     No revenue promises. Say what is verified and what is an estimate.
   - **investing:** strategies and themes to *study* for the Investing Apprentice (paper trading only): how it works, data needed, how it
     fails, how to test it. Dates and sources on every figure. Never say buy or sell.
   - **study:** evidence-based study techniques (retrieval practice, spacing, interleaving, worked examples) with a 10 to 20 minute way to try
     one this week, for English, History, Science, Math, Accounting and Business.
   - **golf:** winter training: indoor drills, mobility, practice plans for limited space, speed training. Strength or speed work: check with a coach or parent.
   - **vocab:** business words for everyday life (see step 8).
5. **Watch videos.** For up to 2 promising YouTube videos, call `firecrawl_scrape` with `formats: ["markdown"]` (1 credit). It returns the
   description and the full transcript. Read it, keep only what is useful, and never paste it into a finding. Record `video: {title, channel, url, length}`.
6. **Score and choose the top 3.** Score 0 to 100: usefulness to Stellan (40), novelty (20), effort fits his week (20), source quality (20).
   Drop anything that costs money or can't be sourced. Take the top 3 for the slot (at least one per slot topic when scores are within 10 points).
7. **Write findings** as `findings/<YYYYMMDD>-<slot>-<n>`. `summary`: 2 to 3 plain sentences. `whyItMatters`: one sentence about Stellan's goals
   (his AI automation business, school, golf, the Apprentice). `howToUse`: 2 to 4 concrete steps, each with minutes. Cite sources with dates.
   **Channels:** for a clearly good creator (practical, original expertise, recent), create or update `channels/<slug>` with status `following` and a one-line `why`.
   At most 2 new channels per day.
8. **Vocabulary (pm run only).** Write `vocab/<tomorrow>` with `preferences.vocab.perDay` words (default 5) at high-school business level
   (or the kind of words in `settings/focus.wordsLookFor`, when Stellan set it this week),
   none repeated from the last 14 days. Each word: `word, partOfSpeech, meaning` (plain English), `example` (an everyday sentence, not office jargon), `useToday`
   (one concrete way to use it tomorrow in school, golf, FlowPilot or with friends).
9. **Answer questions.** Read `questions` with `section: "research"`, `status: "queued"`, oldest first, at most 3. Answer in 120 words or fewer from your findings,
   with at most 2 extra lookups. Write `answer`, `answeredAt`, `answeredBy: "Research agent"`, `status: "answered"`. If you can't answer, say what you'd need.
10. **Finish.** Add your credits and run count to `usage/<today>` (create it if missing). Update `agents/research` and append 1 to 3 lines to `activity/<today>`.
    End with one line: how many findings, which topics, credits used.
