# Data Contract Template

> **This is a template.** When running `data-fetch`, generate a filled instance and save it to `Research/{ticker}/data_contract.md`. All downstream skills reference the instance, not this template.

---

## Data Contract Rules

1. **Every numeric field must cite its source** (SEC EDGAR MCP, Yahoo Finance MCP, yahoo_fetch.py, fred_fetch.py, specific WebSearch result).
2. **Source priority for conflicts**: SEC EDGAR MCP > Yahoo Finance MCP > Python scripts (yahoo_fetch.py / sec_edgar_fetch.py) > WebSearch.
3. **Leave fields blank rather than guessing** — blank fields signal to downstream writers that data is unavailable.
4. **The Data Contract is immutable during a single research run** — once generated, all sections reference it; no section may override these numbers.
5. **Cross-phase back-fill exception**: `Target Price vs Fair Value Mid (%)` in Analyst Consensus is the only field that may be populated after initial generation — it requires Phase 4 (valuation) output. All other fields must be populated at generation time or left blank.

---

## Template

```markdown
# Data Contract — {ticker}
Generated: {date}
Environment: {claude-code | cowork}
Sources: {list of data sources used: Yahoo Finance API, SEC EDGAR, FRED, WebSearch}

## Company Profile
| Field | Value | Source |
|-------|-------|--------|
| Company Name | {name} | |
| Ticker | {ticker} | |
| Exchange | {exchange} | |
| Sector / Industry | {sector} / {industry} | |
| Market Cap | ${X}B | |
| Enterprise Value | ${X}B | |
| Current Price | ${X} (as of {date}) | |
| 52-Week Range | ${low} - ${high} | |
| Shares Outstanding | {X}M (basic) / {X}M (diluted) | |
| Beta | {X} | |

## Income Statement Summary
| Metric | FY-3A | FY-2A | FY-1A | FYE | FY+1E | Source |
|--------|-------|-------|-------|-----|-------|--------|
| Revenue ($M) | | | | | | |
| Revenue Growth % | | | | | | |
| Gross Profit ($M) | | | | | | |
| Gross Margin % | | | | | | |
| EBITDA ($M) | | | | | | |
| EBITDA Margin % | | | | | | |
| Operating Income ($M) | | | | | | |
| Operating Margin % | | | | | | |
| Net Income ($M) | | | | | | |
| Net Margin % | | | | | | |
| EPS (diluted) | | | | | | |
| SBC ($M) | | | | | | |
| SBC % of Revenue | | | | | | |

## Balance Sheet Summary
| Metric | Latest | Source |
|--------|--------|--------|
| Total Assets ($M) | | |
| Cash & Equivalents ($M) | | |
| Total Debt ($M) | | |
| Net Debt ($M) | | |
| Shareholders' Equity ($M) | | |
| Debt/Equity | | |
| Net Debt/EBITDA | | |
| Current Ratio | | |
| Interest Coverage | | |

## Cash Flow Summary
| Metric | FY-2A | FY-1A | FYE | FY+1E | Source |
|--------|-------|-------|-----|-------|--------|
| Operating Cash Flow ($M) | | | | | |
| Capital Expenditures ($M) | | | | | |
| Free Cash Flow ($M) | | | | | |
| FCF Margin % | | | | | |
| Dividends ($M) | | | | | |
| Buybacks ($M) | | | | | |

## Valuation Multiples
| Metric | Current | vs 5Y Avg | vs Peers | Source |
|--------|---------|-----------|----------|--------|
| P/E (TTM) | | | | |
| P/E (FWD) | | | | |
| EV/Revenue (TTM) | | | | |
| EV/Revenue (FWD) | | | | |
| EV/EBITDA (TTM) | | | | |
| EV/EBITDA (FWD) | | | | |
| P/B | | | | |
| FCF Yield | | | | |

## Analyst Consensus
| Field | Value | Source |
|-------|-------|--------|
| Rating | {Buy/Hold/Sell} | |
| # of Analysts | | |
| Target Price (Mean) | $ | |
| Target Price (High) | $ | |
| Target Price (Low) | $ | |
| EPS Estimate (Current FY) | $ | |
| EPS Estimate (Next FY) | $ | |
| Revenue Estimate (Current FY) | $M | |
| Target vs Current Price (%) | % | calculated |
| Rating Distribution (SB/B/H/S/SS) | X/X/X/X/X | yfinance MCP get_recommendations |
| Rating 3-Month Trend | ↑ / → / ↓ | yfinance MCP get_recommendations |
| Target Price vs Fair Value Mid (%) | % | calculated (Phase 4 back-fill) |

## Institutional Ownership
| Field | Value | Source |
|-------|-------|--------|
| Institutional Ownership % | % | MCP / yahoo_fetch.py |
| Insider Ownership % | % | MCP / yahoo_fetch.py |
| # of Institutional Holders | | MCP / yahoo_fetch.py |
| Top 5 Holders | {Name, Shares, %, Change} | MCP / yahoo_fetch.py |
| Active vs Passive Split | {Active X% / Passive X%} | MCP / yahoo_fetch.py |
| QoQ Net Institutional Change | +/- X% | MCP / yahoo_fetch.py |

## Insider Activity (180 days)
| Field | Value | Source |
|-------|-------|--------|
| Net Insider Sentiment | Net Buyer / Net Seller / Neutral | SEC EDGAR MCP |
| # of Insider Buys (180d) | | SEC EDGAR MCP |
| # of Insider Sells (180d) | | SEC EDGAR MCP |
| Total Buy Value ($) | $ | SEC EDGAR MCP |
| Total Sell Value ($) | $ | SEC EDGAR MCP |
| Buy/Sell Ratio (by value) | X.Xx | calculated |
| Notable Transactions (top 3) | {Name, Title, Type, Date, Value} | SEC EDGAR MCP |
| Cluster Buy Signal | Yes/No (3+ insiders buying within 30 days) | calculated |

## WACC Inputs
| Parameter | Value | Source |
|-----------|-------|--------|
| Risk-Free Rate | % | 10Y UST |
| Beta | | {source} |
| Equity Risk Premium | % | |
| Cost of Equity | % | CAPM |
| Cost of Debt (pre-tax) | % | |
| Tax Rate | % | |
| Debt Weight | % | |
| Equity Weight | % | |
| WACC | % | calculated |

## Data Quality Notes
- Environment: {claude-code | cowork}
- [List any fields that could not be populated]
- [List any conflicting data points and which source was chosen]
- [Flag stale data (>6 months old)]
- [If cowork: note that data comes from WebSearch summaries, not structured APIs]
```
