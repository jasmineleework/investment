# Data Contract Template

> **This is a template.** When running `data-fetch`, generate a filled instance and save it to `Research/{ticker}/data_contract.md`. All downstream skills reference the instance, not this template.

---

## Data Contract Rules

1. **Every numeric field must cite its source** (SEC EDGAR MCP, Yahoo Finance MCP, yahoo_fetch.py, fred_fetch.py, akshare_hk_fetch.py, moomoo snapshot, specific WebSearch result).
2. **Source priority for conflicts**: US — SEC EDGAR MCP > Yahoo Finance MCP > Python scripts (yahoo_fetch.py / sec_edgar_fetch.py) > WebSearch. HK — moomoo snapshot (quote-level fields) > Yahoo Finance MCP (statements) > akshare_hk_fetch.py (indicators/dividends; statement cross-validation) > WebSearch. Statement discrepancies >2% between yfinance and AkShare must be flagged in Data Quality Notes.
3. **Leave fields blank rather than guessing** — blank fields signal to downstream writers that data is unavailable.
4. **The Data Contract is append-only during a single research run** — no skill may modify or delete existing rows. Skills may APPEND new rows (e.g., supplemental peer rows) but never overwrite. The report (memo) is a filtered view of the Contract: it may exclude individual peer rows via "Outlier Exclusions" subsections, but the Contract retains every fetched row as audit record.
5. **Append exceptions** (the only sources of new content after initial generation):
   - **Phase 4 back-fill**: `Target Price vs Fair Value Mid (%)` in Analyst Consensus is populated after valuation completes — it requires Phase 4 output.
   - **Peer Data supplement**: the `## Peer Data` section is filled by `data-fetch(mode=supplement, peer_set=[...])`, called from stock-research Step 4.5 after §5a Competitor Identification. Additional supplement calls during §6-§19 or §20 may append more peer rows on demand.
   - **Research Supplement**: the `## Research Supplement` section accepts on-demand WebSearch findings from `data-fetch(mode=supplement, topics=[...])`. Any §X writer (§3, §11, §15, §17, §18, etc.) may trigger this when their section needs additional qualitative material beyond the initial Coverage Log. Entries accumulate; they are never deleted.
   - Outside these three exceptions, all fields must be populated at initial generation time or left blank.

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
| Exchange | {exchange: NYSE/NASDAQ/AMEX/HKEX} | |
| Reporting Currency | {currency; HK: note trading currency HKD vs reporting currency (often RMB) + FX rate used} | |
| ADR Ticker | {HK only: ADR ticker if Level 2/3 dual-listed, else "N/A (OTC or none)"; US: omit row} | |
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

> **HK rule**: HKEX has no free programmatic Form-4 equivalent. Source is HKEXnews
> Disclosure of Interests (Tier 3 WebSearch). If no reportable activity is found,
> fill fields with `N/A (DI checked YYYY-MM-DD, no reportable activity)` — this
> does NOT count as a coverage FAIL. Same convention applies to Institutional
> Ownership fields that yfinance lacks for HK listings.

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
| Risk-Free Rate | % | US: 10Y UST (fred_fetch.py). HK: by cash-flow currency per `references/markets/hk.md` — RMB base → China 10Y (akshare_hk_fetch.py); HKD/USD base → 10Y UST. State which rule applied. |
| Beta | | {source} |
| Equity Risk Premium | % | |
| Cost of Equity | % | CAPM |
| Cost of Debt (pre-tax) | % | |
| Tax Rate | % | |
| Debt Weight | % | |
| Equity Weight | % | |
| WACC | % | calculated |

## Peer Data（MANDATORY — append-only; all rows pulled on research day; no historical reuse）

**Filled by `data-fetch(mode=supplement)`, NOT at initial generation.**
stock-research invokes the supplement call from Step 4.5 (after §5a
Competitor Identification produces the peer set). Subsequent supplement
calls during §6-§19 or §20 may append additional peer rows on demand.

**Append-only**: rows added by supplement calls stay forever — they are
not deleted even if subsequent analysis judges the peer non-comparable.
The report (§20a Comps, §5b Template B) is a filtered view: excluded
peers are documented in "Outlier Exclusions" subsections, but the
Contract retains the row as audit record.

**Pull Date == research day (today)**: every row in this section must
have `Pull Date` equal to today. Supplement calls refresh any stale
rows in-place to maintain this invariant across the whole section. If
any row's Pull Date ≠ today, validate_data_contract.py reports FAIL —
trigger a supplement call to refresh.

| Ticker | Price | Shares (M, diluted) | Market Cap ($B) | FY{YYYY}A Revenue ($M) | TTM EBITDA ($M) | Net Income ($M) | Net Debt ($M) | Source | Pull Date (YYYY-MM-DD) |
|--------|-------|---------------------|-----------------|------------------------|------------------|------------------|---------------|--------|--------------------------|
|        |       |                     |                 |                        |                  |                  |               | yfinance MCP | |
|        |       |                     |                 |                        |                  |                  |               |               | |

Rules:
- Minimum 5 peer rows, maximum 8
- Every numeric cell must be filled or marked `N/A — data source unavailable`; **never use "~", "约", "approximately", or training-memory estimates**
- `Pull Date` column must equal research day (today). 7-day tolerance windows or snapshot reuse are prohibited
- If a peer's MCP fetch fails, mark the row `N/A — MCP fetch failed YYYY-MM-DD` and exclude from §20a median calculations

## Research Supplement（append-only; on-demand qualitative WebSearch findings）

**Filled by `data-fetch(mode=supplement, topics=[...])`.** Any analytical section writer (e.g., §15 Data & AI Economics needs specifics on a new chip launch; §17 Supply Chain needs a supplier disclosure; §18 Risk Inventory needs litigation timeline) may invoke a supplement call with a topic list when the initial Coverage Log doesn't have enough material. Entries accumulate across the research run as different sections surface different needs.

**Format**: one block per topic, in chronological order of when the supplement call was made.

### {Topic 1 string} — {YYYY-MM-DD}
- Triggered by: §X {section name}
- Query: "{the actual WebSearch query used}"
- Findings:
  - {finding 1 with inline source}: [source title](url) ({source date})
  - {finding 2 with inline source}: [...]
  - {finding 3 with inline source}: [...]

### {Topic 2 string} — {YYYY-MM-DD}
- Triggered by: §X {section name}
- Query: "..."
- Findings:
  - ...

Rules:
- Append-only — never edit or delete a prior block (it's part of the audit trail)
- Each block must record: topic, date the supplement call was made, triggering §section, the WebSearch query verbatim, and 3-5 findings with source URL + date
- Findings may be cited in §X prose; cite the Research Supplement block reference (e.g., "see Research Supplement 2026-05-19 #1") in the section text
- Coverage Log captures the same URLs; Research Supplement adds the context (which section triggered it and why)

## Data Quality Notes
- Environment: {claude-code | cowork}
- [List any fields that could not be populated]
- [List any conflicting data points and which source was chosen]
- [Flag stale data (>6 months old)]
- [If cowork: note that data comes from WebSearch summaries, not structured APIs]
```
