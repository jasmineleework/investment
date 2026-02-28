# Data Contract Template

> **This is a template.** When running `data-fetch`, generate a filled instance and save it to `Research/{ticker}/data_contract.md`. All downstream skills reference the instance, not this template.

---

## Data Contract Rules

1. **Every numeric field must cite its source** (SEC EDGAR MCP, Yahoo Finance MCP, yahoo_fetch.py, fred_fetch.py, specific WebSearch result).
2. **Source priority for conflicts**: SEC EDGAR MCP > Yahoo Finance MCP > Python scripts (yahoo_fetch.py / sec_edgar_fetch.py) > WebSearch.
3. **Leave fields blank rather than guessing** — blank fields signal to downstream writers that data is unavailable.
4. **The Data Contract is immutable during a single research run** — once generated, all sections reference it; no section may override these numbers.

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
