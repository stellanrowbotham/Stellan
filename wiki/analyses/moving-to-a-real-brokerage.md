---
type: analysis
title: Moving the apprentice to a real brokerage
aliases: ["Real-money plan", "Brokerage plan", "Going live"]
tags: [investing, agents, plan]
question: What would it take to move the Investing Apprentice from simulation to a real brokerage account?
status: thinking stage (nothing connected)
created: 2026-10-16
updated: 2026-10-16
sources: [src-stellan-investing-apprentice-brief]
---

# Moving the apprentice to a real brokerage
> Filed from a request on 2026-10-16: "start thinking about moving into a brokerage" *(Stellan, 2026-10-16)*. **Nothing real is connected. This is a plan only.**

## Answer: four gates, in order
### 1. Prove the strategy first (now to about 3 months)
- The first week was 2 crypto trades and a −0.8% change in account value, which is far too little to judge anything *(synthesis)*.
- The brief says no amount of simulated success should automatically unlock live trading, and any real-money module stays off until Stellan approves it separately ([[src-stellan-investing-apprentice-brief]]).
- Suggested bar *(synthesis)*:
  - at least 3 months with working stock data;
  - at least 30 closed trades;
  - beating the XIU benchmark after fees;
  - no single trade making most of the profit.

### 2. An adult account holder
- Opening a brokerage account in Canada requires the age of majority (18 or 19, depending on the province) *(general knowledge)*.
- A parent or guardian would need to open the account and stay involved *(synthesis)*.

### 3. A broker that allows it
| Option | Can a personal program place orders? | Notes |
|---|---|---|
| **Questrade** | **No.** Order placement through the API is for approved partner developers only; customers get account and market data | [Questrade API](https://www.questrade.com/api/home), [API access agreement](https://www.questrade.com/disclosure/legal-notice-and-disclosures/api-access-agreement) |
| Wealthsimple | No official public trading API *(general knowledge, unverified)* | |
| Interactive Brokers (IBKR) Canada | Has a trading API used by individuals *(general knowledge, unverified)* | Needs its own check of fees, minimums and account rules |
| **Human-in-the-loop** (any broker) | Not needed | The apprentice proposes, a person places the order by hand. This is the same pattern as the Investopedia order slips |

**Best first step:** human-in-the-loop with a parent-held account. The apprentice emails an order slip, and a person decides and places it. This also matches the brief's rule that every real trade needs explicit human approval ([[src-stellan-investing-apprentice-brief]]) *(synthesis)*.

### 4. Safeguards before any automatic orders
From the brief ([[src-stellan-investing-apprentice-brief]]):
- a clear explanation of the extra risks;
- a review of independently checked results;
- a review of the broker's API permissions;
- approval of each exact trade;
- position and loss limits;
- a kill switch;
- secure credential storage;
- an audit log;
- a way to disconnect the account.
All of this would be a **separate module** with its own approval. The current code has no live-trading path ([[investing-apprentice]]).

## Basis
- Pages used: [[investing-apprentice]], [[investing-apprentice-plan]], [[risk-management]], [[src-stellan-investing-apprentice-brief]]
