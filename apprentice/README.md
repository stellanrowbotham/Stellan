# Investing Apprentice

A **simulation-only** AI research and paper-trading agent for Canadian and US stocks, ETFs and
crypto. It starts as a Level 1 Research Apprentice with a pretend **$1,000 CAD** account, and earns
promotions only through measured, documented evidence plus Stellan's approval.

There is **no live-trading code** and **no brokerage connection**. Simulated success never unlocks
real money. Any real-money module would be a separate project with its own approval process.

- Dashboard (private): https://claude.ai/artifact/PHFxL9AAwnp1DRxWzXLMUQ (page source: `apprentice/web/index.html`)
- Plan and design decisions: `wiki/analyses/investing-apprentice-plan.md`
- What the scheduled runs do: `apprentice/ROUTINE_GUIDE.md`

## How it fits together
```
config/ (protected, hash-approved)   settings.json · universe.json · sources.json · feeds.json
providers/   Bank of Canada · Kraken · CoinGecko · DefiLlama · Twelve Data · Alpha Vantage · Finnhub · FRED · SEC EDGAR · RSS
collect.py   scheduled collection → ledger/quotes, ledger/research, ledger/source_checks
validate.py  bad/stale/future-dated data, cross-source conflicts, look-ahead checks
research.py  agent research notes (fact / estimate / opinion / ai_interpretation), syndication dedupe
forecasts.py forecasts recorded before outcomes; Brier scoring; calibration
scoring.py   documented 0-100 candidate score + pass/fail gates ("No trade" when nothing passes)
risk.py      code-enforced risk limits (position, sector, crypto, risk-per-trade, halts, level, freshness)
broker.py    paper broker: the only thing that creates fills (no network code, real stored quotes only)
costs.py     Questrade-like stock costs (FX fee on US), Kraken-like crypto fees, spread and slippage
portfolio.py accounting rebuilt from fills; reconciliation check
reviews.py   8-question post-trade reviews; rule compliance computed by code
promotion.py promotion eligibility (with reasons) and automatic demotions
scorecard.py rewards and penalties from a fixed table (nothing for volume)
backtest.py  walk-forward, out-of-sample testing for proposed strategy changes
report.py    plain-language Markdown and HTML report
dashboard.py JSON for the dashboard + CSV exports
health.py    ledger integrity, accounting, config approval, stale data, integrations, missed jobs
ledger/      append-only, hash-chained JSON-lines records (the source of truth)
```

## Setup (things only Stellan can do)

### 1. Allow the data sites in the cloud environment's network settings
On 2026-10-10 the environment's network policy blocked every data host. Open the cloud environment
menu in the session's title bar, then **Edit → Network access**. Either pick a broader access level, or
add these under **Allowed domains** (keep "Allow package managers" ticked). Steps:
https://code.claude.com/docs/en/cloud-environments#network-access

```
www.bankofcanada.ca        api.kraken.com            api.coingecko.com        api.llama.fi
api.twelvedata.com         www.alphavantage.co       finnhub.io               api.stlouisfed.org
www.sec.gov                data.sec.gov              www.cnbc.com             feeds.content.dowjones.io
finance.yahoo.com          www.investing.com         www.federalreserve.gov   www.coindesk.com
cointelegraph.com          decrypt.co                www.theblock.co          blog.kraken.com
```

### 2. Get free API keys and add them as environment variables
Add them in the same environment settings, as environment variables or network secrets. Never paste
keys into chat or commit them.

| Variable | Where to get it (free) | Used for |
|---|---|---|
| `TWELVEDATA_API_KEY` | twelvedata.com → sign up → API key | TSX and US quotes, daily history |
| `ALPHAVANTAGE_API_KEY` | alphavantage.co/support/#api-key | TSX fallback (.TRT), 25 calls/day |
| `FINNHUB_API_KEY` | finnhub.io → register | US quotes, earnings calendar |
| `FRED_API_KEY` | fredaccount.stlouisfed.org → API keys | US inflation, jobs, rates, oil |
| `COINGECKO_DEMO_API_KEY` | coingecko.com/en/api → Demo plan | Crypto market caps, 24h volume |
| `SEC_USER_AGENT` | no signup: set it to e.g. `Stellan Rowbotham your-email@example.com` | SEC EDGAR requires a contact |

Bank of Canada, Kraken, DefiLlama and the RSS feeds need no key, only the network allowance.

### 3. Check it works
```bash
python3 -m apprentice collect     # every source should say ok, or explain why not
python3 -m apprentice sources     # live status of all 48 registry entries
```

## Commands
```bash
python3 -m unittest discover -s tests/apprentice -t . -v   # 56 tests: costs, accounting, timestamps, risk, promotions, no-live-trading
python3 -m apprentice status | health | verify | sources
python3 -m apprentice --help                               # every command
```
No third-party packages: Python 3.11+ standard library only. No database server: the ledgers are
plain files in git, so the history is auditable and any edit to an old record breaks the hash chain.

## Changing the rules (Stellan only)
Risk limits, the asset universe, promotion thresholds and the current level live in
`config/settings.json` and `config/universe.json`. Their combined hash is stored in
`config/approved.sha256`. If either file changes without a matching approval, **all simulated trading
locks** and CI fails. To change something:
1. Ask Claude in an interactive chat.
2. Approve the exact change.
3. Claude edits the file and runs `python3 -m apprentice approve-config`, which refuses to run inside a
   scheduled Routine.

**Promotions work the same way.** When the dashboard says "eligible", Stellan decides, and the level
changes only through an approved config edit. Demotions are automatic.

Be aware this is *tamper-evident*, not tamper-proof: someone with write access to the repo could
change both files. The protections are that the Routine's instructions forbid it, every change shows
up in git history, the CI check fails, and the dashboard shows "settings changed without approval".

## Known limitations (be honest about these)
- Fee figures are **unverified** (taken from secondary reviews on 2026-10-10). Check them against
  Questrade's and Kraken's official fee pages before relying on cost results.
- Holiday calendars cover 2026–2027 and must be checked against the TMX and NYSE calendars. Dates
  outside that range fail safe (treated as closed).
- Free price data may be delayed up to about 15 minutes, and TSX coverage on free plans is unconfirmed.
- Stops are checked only when a run happens, so a price that dips through a stop and recovers
  between runs is missed. A gap through a stop fills at the real, worse price.
- Questrade fractional shares are modelled as unavailable, so the $100 position cap excludes
  stocks priced over $100.
- The day-trading strategy is a labelled hourly **experiment**, not real day trading.
