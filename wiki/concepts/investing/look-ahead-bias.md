---
type: concept
title: Look-ahead bias
aliases: ["Peeking", "Future leakage", "Hindsight bias in backtests"]
tags: [investing]
created: 2026-10-10
updated: 2026-10-10
sources: [src-stellan-investing-apprentice-brief]
---

# Look-ahead bias
Accidentally using information from the future when judging a past decision, which makes a strategy look smarter than it really is.

## In plain words
Imagine betting on a hockey game after you've already seen the score. You'd win every time, but you didn't really predict anything. In investing, it's easy to cheat like that by mistake, for example by using a news story published at 10 AM to "decide" a trade at 9 AM *(general knowledge)*.

## Explanation
Every piece of data gets two timestamps: when it was **published or observed**, and when it was **used**. A decision may only use data whose publication time is before the decision time. That means snapshots of prices and news are stored as they were seen, not re-downloaded later. Re-downloaded data can be revised, such as restated earnings or corrected economic figures ([[src-stellan-investing-apprentice-brief]]).

## Evidence & claims
- The paper trader "must never use information published after its simulated decision time when evaluating that decision" ([[src-stellan-investing-apprentice-brief]]).
- Acceptance test 3: simulated trades use only information available at decision time ([[src-stellan-investing-apprentice-brief]]).

## Tensions & contradictions
- None yet.

## Related
- [[paper-trading]], [[source-reliability]]
