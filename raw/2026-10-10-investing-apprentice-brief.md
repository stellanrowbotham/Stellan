<!-- captured: 2026-10-10 | origin: pasted by Stellan | author: Stellan Rowbotham | published: 2026-10-10 | note: pasted into a Claude Code chat; content kept as given -->

Build an AI Stock & Crypto Investing Apprentice
1. Your Role
Act as a senior AI engineer, financial data engineer, quantitative research developer, and product designer.
I want you to help me build a personal AI investing agent that learns about the stock market and cryptocurrency through research, simulated trading, performance tracking, and self-evaluation.
This should not be a basic chatbot that tells me which stocks to buy. I want a complete investing research and paper-trading system that operates like an apprentice working toward becoming a highly capable investment analyst.
The agent should begin with no trading privileges, develop its research and analytical abilities, make simulated investment decisions, track the results over time, learn from mistakes, and earn promotions through a transparent performance-based system.
Your first task is to interview me about exactly what I want. Do not start building the application until you understand my requirements and I approve the proposed plan.
2. Phase One: Interview Me Before Building
Start by asking me the questions you need to understand my vision.
Ask clear, straightforward questions. You can ask follow-up questions based on my answers. Group related questions together so the process is organized and easy to follow.
Cover these topics:

* My goals: Am I trying to learn investing, maximize simulated returns, understand market movements, or accomplish all three?
* Markets: Which stock exchanges, individual stocks, ETFs, cryptocurrencies, and other assets should the agent research?
* Research sources: Which financial news outlets, company filings, earnings reports, economic indicators, analyst research, market data providers, and other sources should it use?
* Trading style: Should it focus on day trading, swing trading, long-term investing, or test multiple strategies?
* Risk management: What simulated starting balance, maximum position size, loss limits, and portfolio diversification rules should apply?
* Research frequency: Should it run once daily, continuously during market hours, or at another schedule?
* Simulation: Should it simulate individual trades, build a diversified portfolio, or support both?
* Learning: How should it record mistakes, compare strategies, evaluate its predictions, and improve its research process?
* Promotions: What performance standards should an agent meet before advancing to the next level?
* Dashboard: What information, charts, reports, notifications, and performance statistics do I want to see?
* Technology: Where should it run, which AI models should power it, and what APIs or services can I access?
* Future permissions: What additional capabilities might I eventually want, and what safeguards must be in place before any real-money trading is considered?

Ask additional questions whenever an answer would materially change the design.
Do not make me answer questions whose answers can be researched or determined from the available technical environment.
After the interview, summarize my requirements, identify any unresolved decisions, recommend a technical architecture, and present a phased development plan. Wait for my approval before implementing it.
3. Phase Two: Build the Research Engine
Build an agent that gathers and analyzes reliable, relevant, current financial information.
It should research both stocks and cryptocurrency, using the sources and assets I approve.
Research capabilities
The agent should be able to:

1. Retrieve current and historical market prices.
2. Review financial news and identify potentially market-moving events.
3. Analyze company earnings, revenue growth, profitability, valuation, debt, cash flow, and other relevant fundamentals.
4. Study price trends, trading volume, volatility, momentum, and other technical indicators.
5. Monitor economic conditions, interest rates, inflation, employment data, and relevant central bank announcements.
6. Research cryptocurrency market conditions, project fundamentals, network activity where reliable data is available, token supply, liquidity, and major developments.
7. Identify upcoming earnings reports, economic announcements, token unlocks, and other relevant events.
8. Compare possible investments and explain why one candidate may be more attractive than another.
9. Identify bearish evidence, risks, contradictory information, and reasons a proposed trade might fail.
10. Maintain a watchlist of promising assets and track changes in their investment cases.

Research quality requirements

* Use reliable data providers and reputable sources.
* Cite sources and provide publication dates and data timestamps.
* Distinguish verified facts from estimates, opinions, and AI-generated interpretations.
* Verify important claims using independent sources when possible.
* Detect stale, missing, conflicting, or suspicious data.
* Never invent stock prices, news, financial figures, or research citations.
* Clearly disclose when the available evidence is insufficient.
* Respect API terms, rate limits, authentication requirements, and website access restrictions.
* Never claim to have searched the entire internet. Explain which sources and datasets were actually searched and what their limitations are.

The agent should prioritize useful research over collecting enormous amounts of irrelevant information.
4. Phase Three: Daily Investment Research Report
At the frequency I choose, generate an investment research report based on information available at that time.
For every potential investment, include:

* Asset name, ticker, and asset type.
* Current or latest available price and its timestamp.
* Why the asset is being considered.
* Important news and fundamental developments.
* Technical indicators and relevant price levels.
* Potential catalysts and upcoming events.
* Bullish and bearish arguments.
* Main risks and what could invalidate the investment thesis.
* Proposed entry price or entry conditions.
* Potential exit conditions and profit-taking rules.
* A proposed stop-loss or risk-control plan where appropriate.
* Intended holding period.
* Suggested simulated position size.
* Expected upside and downside scenarios.
* Confidence level supported by measurable evidence.
* Links to the underlying sources.

Rank the strongest candidates using a documented scoring system.
Do not force the agent to recommend a trade every day. If no opportunity meets the required standards, it should say "No trade: current opportunities do not meet the required criteria."
A research recommendation is a hypothesis, not a guarantee of profit. The agent must explain uncertainty and avoid treating a high confidence score as proof that a trade will succeed.
5. Phase Four: Build a Realistic Paper-Trading Simulator
The agent must begin in simulation mode, with no ability to place real orders.
Create a simulated portfolio using a starting balance that I choose during the interview.
The system should simulate buying and selling assets using real market data, while keeping all transactions virtual.
Every simulated trade must record

* Trade ID.
* Asset and ticker.
* Decision timestamp.
* Data available when the decision was made.
* Simulated entry price.
* Number of shares or units.
* Position size and transaction costs.
* Original investment thesis.
* Expected holding period.
* Planned exit rules.
* Actual exit price when closed.
* Realized profit or loss.
* Unrealized profit or loss while open.
* Holding period.
* Whether the original thesis was correct.
* Lessons learned after the trade.

Include realistic trading frictions, such as commissions where applicable, bid-ask spreads, slippage, and crypto trading fees. Respect market hours, holidays, order types, and asset-specific trading restrictions.
Never assume a simulated order could execute at a price that was unavailable at the time. Handle gaps, missing price data, and after-hours trading explicitly.
Prevent look-ahead bias: the agent must only use information that was available when the simulated decision was made.
For cryptocurrencies, account for continuous trading, different exchange prices, liquidity, and the fact that trading costs vary by platform.
Portfolio dashboard
Show:

* Starting virtual balance.
* Current cash balance.
* Open positions.
* Total portfolio value.
* Total return and percentage return.
* Realized and unrealized profit or loss.
* Daily, weekly, and monthly performance.
* Maximum drawdown.
* Win rate.
* Average winning and losing trade.
* Profit factor.
* Risk-adjusted performance where sufficient data exists.
* Performance against suitable benchmarks.
* Trading fees and simulated slippage.
* Best and worst trades.
* Performance by asset, strategy, and holding period.

Include downloadable trade history and historical portfolio performance.
6. Phase Five: Make the Agent Learn From Its Results
I want the agent to improve through a structured learning process, not through unsupported claims that it is getting smarter.
After each completed trade, the agent should conduct a post-trade review.
It should answer:

1. What was the original hypothesis?
2. What evidence supported the decision?
3. What happened afterward?
4. Which assumptions were correct or incorrect?
5. Did the result reflect a sound process, luck, or an identifiable mistake?
6. Were the entry, position size, and exit consistent with the rules?
7. What should be tested differently next time?
8. Is there enough evidence to change the strategy?

Maintain a persistent research journal and a versioned strategy library.
Store previous forecasts, original reasoning, data timestamps, results, and lessons learned. Do not overwrite old predictions after seeing the outcome.
The agent may propose improvements to its strategies, scoring rules, or research process. However, it must test significant changes in a separate evaluation environment before adopting them.
Use out-of-sample testing, walk-forward validation, and realistic transaction costs where appropriate. Compare proposed changes with the existing strategy and relevant benchmarks.
Do not allow the agent to rewrite its own safeguards, grant itself permissions, fabricate performance history, or change evaluation rules to make its results look better.
Reward sound decision-making as well as profitable outcomes. A losing trade can be a good decision if it followed a valid process, and a winning trade can be a bad decision if it relied on unjustified risk.
7. Phase Six: The Promotion and Reward System
Create a progression system that makes the agent earn its advancement.
The agent starts as a Level 1 Apprentice and advances only after satisfying predefined, measurable requirements.
Use the following as a proposed structure. Final thresholds must be configurable and approved before implementation.
Level 1: Research Apprentice
Responsibilities:

* Learn the data sources and research process.
* Summarize market developments.
* Explain financial concepts.
* Build watchlists and record hypotheses.
* Make forecasts without executing simulated trades until the initial research process is validated.

Promotion evidence:

* Reliable sourcing.
* Accurate timestamps.
* Complete research records.
* No fabricated data or missing required disclosures.

Level 2: Paper-Trading Apprentice
Responsibilities:

* Begin virtual trading.
* Track entries, exits, costs, and outcomes.
* Complete post-trade reviews.

Promotion evidence:

* Minimum required observation period.
* Sufficient completed trades.
* Consistent risk controls.
* Auditable trade records.

Level 3: Research Analyst
Responsibilities:

* Compare strategies.
* Analyze fundamentals and technical indicators.
* Test ideas against appropriate benchmarks.
* Produce more detailed investment reports.

Promotion evidence:

* Positive results under predefined evaluation conditions, or a demonstrated improvement in risk-adjusted performance.
* Acceptable drawdown.
* Results that are not dependent on one lucky trade or one unusually favorable market period.
* Credible out-of-sample results.

Level 4: Senior Analyst
Responsibilities:

* Manage a simulated portfolio under stricter risk limits.
* Evaluate different market conditions.
* Monitor strategy degradation.
* Recommend changes supported by evidence.

Promotion evidence:

* Sustained performance across multiple evaluation periods.
* Consistent adherence to risk controls.
* Stable results after realistic trading costs.
* No material violations of the research process.

Level 5: Trusted Research Agent
Responsibilities:

* Produce independently evaluated investment research.
* Maintain a transparent performance history.
* Explain its decisions and uncertainties.
* Recommend whether a trade meets the approved simulated strategy's criteria.

Reaching this level does not automatically grant real-money trading permission.
Promotion rules

* Every promotion must be based on a documented evaluation.
* Minimum trade counts and observation periods must be configurable.
* Evaluate returns relative to suitable benchmarks and risk taken.
* Use a held-out test set or forward-testing period to reduce overfitting.
* Account for different market conditions and trading costs.
* Include penalties for excessive risk, poor data quality, broken rules, and unreliable reporting.
* Require human approval for promotions that change the agent's capabilities or permissions.
* Display exactly why the agent passed or failed each requirement.

The agent must never receive a promotion solely because it generated a high return over a short period.
8. Phase Seven: Learning Rewards and Accountability
Give the agent a virtual scorecard and a reward system.
Rewards may include:

* Promotion to the next research level.
* Access to additional approved research tools.
* Permission to test more advanced strategies in isolated simulations.
* Higher simulated portfolio limits after passing risk evaluations.
* Recognition for improving forecast accuracy and research quality.

Penalties may include:

* Losing points for fabricated facts or unsupported conclusions.
* Failing an evaluation after breaking a risk rule.
* Losing promotion eligibility after an integrity violation.
* Returning to a supervised level if performance deteriorates.

Keep a visible record of every reward, penalty, promotion, demotion, and reason.
Do not reward activity for its own sake. More trades, more research volume, and more confident predictions should not automatically earn points.
The goal is to reward disciplined analysis, accurate record-keeping, risk management, and evidence-based improvement.
9. Phase Eight: Separate Real-Money Trading From Simulation
This project must be simulation-only by default.
Do not connect a live brokerage account, request brokerage trading credentials, or place real orders during initial development.
Design the system so that the research engine, paper-trading engine, and any future live execution module are separate components.
If I eventually decide to explore real-money trading, first require a separate approval process that includes:

* A clear explanation of the additional risks.
* A review of the agent's independently verified performance.
* A review of the brokerage API and its permissions.
* Explicit human approval of the exact proposed trade.
* Maximum position and loss limits.
* A kill switch that immediately disables order submission.
* Secure credential management.
* An audit log of every authorized action.
* A way to revoke access and disconnect the brokerage.

No amount of simulated success should automatically unlock live trading.
Do not let the agent transfer virtual funds into a real account or execute a live transaction on its own initiative. Any future real-money functionality must remain disabled until I explicitly approve the separate implementation and its safeguards.
Because I am learning about investing, prioritize financial education and transparent explanations over aggressive trading or promises of profit.
10. Phase Nine: Build the Dashboard
Build a polished, professional web application that makes the agent feel like a serious financial research platform.
The dashboard should include:
Overview

* Virtual account balance.
* Daily and total simulated returns.
* Portfolio performance chart.
* Current positions.
* Latest market developments.
* Agent level and promotion progress.

Research

* Ranked investment candidates.
* Full research reports.
* Source links and timestamps.
* Bullish and bearish evidence.
* Risks, scenarios, and confidence explanations.

Paper Trading

* Open and closed positions.
* Virtual orders.
* Trade history.
* Profit-and-loss breakdowns.
* Fees, slippage, and portfolio exposure.

Learning Center

* Post-trade reviews.
* Forecast accuracy.
* Strategy comparisons.
* Mistake journal.
* Lessons learned.
* Experiments awaiting approval.

Progression

* Current level.
* Promotion requirements.
* Progress toward each requirement.
* Rewards and penalties.
* Evaluation history.
* Reasons for passing or failing.

Settings

* Research schedule.
* Approved assets.
* Risk limits.
* Data sources.
* Starting virtual balance.
* Benchmark selection.
* Notifications.
* Agent permissions.

The interface should feel premium, clean, responsive, and data-rich without becoming cluttered. Use interactive charts, useful filtering, clear tables, and understandable explanations. Avoid fake performance numbers and decorative statistics that do not represent real data.
11. Phase Ten: Technical Architecture and Reliability
Before choosing technologies, inspect the available development environment and research the current documentation for appropriate data providers, APIs, AI models, and financial tools.
Recommend a maintainable architecture with separate modules for:

* Market data collection.
* News and research retrieval.
* Data validation and timestamping.
* Investment analysis.
* Strategy evaluation.
* Paper-trade execution.
* Portfolio accounting.
* Learning and post-trade review.
* Promotion and reward logic.
* Notifications.
* Dashboard and reporting.
* Security, audit logs, and permissions.

Use persistent storage for trades, prices, decisions, forecasts, research sources, strategy versions, and promotion history.
Include automated tests for calculations, transaction costs, portfolio accounting, timestamps, order execution rules, risk limits, and promotion criteria.
Use secure environment variables for API keys. Never expose secrets in frontend code, logs, source control, or generated reports.
Build monitoring for failed data requests, stale prices, API limits, broken scheduled jobs, and inconsistent portfolio records.
Do not pretend an API is connected if it has not been configured. Clearly label missing integrations and provide setup instructions.
Use a modular design so that new data sources, assets, research strategies, and evaluation methods can be added without rebuilding the entire application.
12. Phase Eleven: Development and Acceptance Tests
Develop the application in small, testable phases.
Before declaring the application complete, demonstrate that:

1. The agent can collect and timestamp valid market data.
2. Research reports link to the actual sources used.
3. Simulated trades use only information available at decision time.
4. The virtual balance, position quantities, and profit-and-loss calculations reconcile correctly.
5. Transaction costs are included.
6. Closed trades retain their original forecasts and reasoning.
7. Post-trade reviews use actual recorded outcomes.
8. Promotion decisions follow the documented criteria.
9. The agent cannot change its own permissions or bypass risk limits.
10. No real order can be placed through the simulation system.
11. Missing data and API failures are handled safely.
12. The dashboard accurately reflects the stored records.
13. All important calculations and permissions have automated tests.

Provide setup instructions, required environment variables, database configuration, test commands, and instructions for running the application locally or deploying it.
Never use fabricated historical results as evidence of actual performance. If demonstration data is necessary, label it clearly as fictional.
13. Your First Response
Do not begin writing the application code yet.
First, interview me about the project. Ask the questions that matter most, adapt your follow-up questions to my answers, and help me make informed decisions when I do not know the technical terminology.
After we finish the interview:

1. Summarize my exact vision.
2. Identify the features that belong in the first version and those that can wait.
3. Recommend suitable technologies and data providers.
4. Explain likely operating costs, API limitations, and maintenance requirements.
5. Present the proposed architecture and development phases.
6. Explain how simulation accuracy, learning, and promotions will be measured.
7. Identify security risks and safeguards.
8. Ask me to approve the plan before implementation.

The final goal: Build an AI investing apprentice that studies the market, makes documented simulated investment decisions, tracks what would have happened, learns from evidence, and earns every promotion. I want to use it to improve my own investing knowledge and discover whether its strategies have genuine value, without risking real money during the learning stage.   Financial Research Source Library and Daily Data Collection
Integrate a source library containing at least 45 financial research sources and providers across stock-market journalism, official company disclosures, stock exchanges, economic data, financial APIs, cryptocurrency news, and crypto market data.
Use the following sources as the initial approved library:
Stock-market journalism

1. Reuters Markets — https://www.reuters.com/markets/
2. Bloomberg Markets — https://www.bloomberg.com/markets
3. CNBC Markets — https://www.cnbc.com/markets/
4. Financial Times — https://www.ft.com/markets
5. The Wall Street Journal — https://www.wsj.com/news/markets
6. MarketWatch — https://www.marketwatch.com/
7. Yahoo Finance — https://finance.yahoo.com/
8. Associated Press Business — https://apnews.com/hub/business
9. Barron's — https://www.barrons.com/
10. Investing.com — https://www.investing.com/

Official disclosures and exchanges

11. SEC EDGAR — https://www.sec.gov/search-filings
12. Nasdaq — https://www.nasdaq.com/market-activity
13. NYSE — https://www.nyse.com/market-data
14. TMX — https://www.tsx.com/
15. Company investor-relations websites and official earnings releases.
16. FINRA — https://www.finra.org/finra-data
17. CFTC — https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
18. TradingView — https://www.tradingview.com/

Economic information

19. Federal Reserve — https://www.federalreserve.gov/newsevents.htm
20. FRED — https://fred.stlouisfed.org/
21. US Bureau of Labor Statistics — https://www.bls.gov/
22. US Bureau of Economic Analysis — https://www.bea.gov/
23. US Treasury — https://home.treasury.gov/
24. Bank of Canada — https://www.bankofcanada.ca/
25. Statistics Canada — https://www.statcan.gc.ca/
26. US Energy Information Administration — https://www.eia.gov/

Financial-data providers

27. Alpha Vantage — https://www.alphavantage.co/
28. Massive — https://massive.com/
29. Finnhub — https://finnhub.io/
30. Financial Modeling Prep — https://site.financialmodelingprep.com/
31. Twelve Data — https://twelvedata.com/
32. Tiingo — https://www.tiingo.com/
33. Nasdaq Data Link — https://data.nasdaq.com/
34. StockAnalysis — https://stockanalysis.com/

Cryptocurrency research

35. CoinDesk — https://www.coindesk.com/
36. CoinGecko — https://www.coingecko.com/
37. CoinMarketCap — https://coinmarketcap.com/
38. Cointelegraph — https://cointelegraph.com/
39. Decrypt — https://decrypt.co/
40. The Block — https://www.theblock.co/
41. CoinDesk Data API — https://developers.coindesk.com/
42. CoinGecko News API — https://www.coingecko.com/en/api/news
43. Coinbase — https://www.coinbase.com/blog
44. Kraken — https://blog.kraken.com/
45. DefiLlama — https://defillama.com/

Source integration requirements
Do not assume that every website provides an API, free access, real-time prices, or permission to scrape its content. Verify the current documentation, access terms, API pricing, rate limits, and data freshness before implementing each integration.
Prioritize official filings and company announcements for primary facts; reputable news organizations for market-moving events; official economic agencies for macroeconomic releases; and licensed market-data providers for price and trading information.
Build a source registry that records each provider's name, category, URL, integration method, access status, last successful retrieval time, publication timestamp, data timestamp, reliability tier, and any known limitations.
Implement scheduled collection and event-driven updates where supported. For daily reporting, collect relevant information before the selected reporting time and update it as new material information becomes available.
Deduplicate syndicated stories, track the original publication time, and distinguish original reporting from commentary or reposts.
For important claims, seek corroboration from independent sources. Prefer original company filings and official announcements over headlines that merely repeat another publication.
Do not count multiple websites republishing the same story as independent confirmation.
Store historical snapshots of market data, research inputs, and decision timestamps. The paper-trading agent must never use information published after its simulated decision time when evaluating that decision.
If a source is unavailable, stale, paywalled, or requires an API key, record the limitation and continue with approved alternatives. Never fabricate retrieved data or claim that an integration is operational when it is not.
Before recommending a simulated trade, verify that the asset price is sufficiently current for the chosen trading strategy and that the supporting research is available. If reliable information is missing, postpone the decision or abstain from trading.
The objective is not to consume the maximum number of sources. It is to produce accurate, timely, independently checked, traceable investment research with realistic paper-trading results. the make that agent then clean out the LLm Wiki database and add in this agent and add in all of me egsisting agents
