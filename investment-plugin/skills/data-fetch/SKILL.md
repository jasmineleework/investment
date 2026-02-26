---
name: data-fetch
description: >
  Financial data collection for investment research.
  Collects structured data via MCP APIs (primary), WebSearch (secondary),
  and SEC filings. Outputs a Data Contract file consumed by all
  downstream skills.
---

# Data Fetch

Collect and validate financial data for a given stock ticker. This skill is called by `stock-research` or `quick-check` and should not be invoked directly by the user.

## Inputs

- `{ticker}` — Stock ticker symbol (e.g., AAPL)
- `{market}` — Market identifier (default: US)
- `{mode}` — `"full"` (default, for /research) or `"quick"` (for /quick-check)

## Outputs

1. **Data Contract** — Standardized financial metrics file (markdown table). ALL downstream sections MUST reference this file for quantitative data, not re-derive from memory.
2. **Web source list** — Coverage Log (full mode targets 30+ unique sources)
3. **Coverage Validator** — Pass/fail for each criterion (full mode only)

---

## Step 1: Structured Financial Data (MCP APIs)

### Priority 1 — MCP Data Providers (try in order, use first available)

Check for these MCP tools at runtime. Use the FIRST available provider:

| Priority | Provider | MCP Server | Key Data |
|----------|----------|------------|----------|
| 1 | S&P Global / Kensho | `spglobal` | Financials, estimates, ownership, transcripts |
| 2 | FactSet | `factset` | Market data, estimates, fundamentals |
| 3 | Morningstar | `morningstar` | Financials, ratings, fair value |
| 4 | LSEG | `lseg` | Market data, indices |
| 5 | Daloopa | `daloopa` | Detailed financials, alternative data |

**How to detect**: List available MCP tools. If any tool name contains the provider keyword (e.g., `spglobal`, `factset`), that provider is available.

**If an MCP provider is available**, query it for:

```
- Company profile (name, sector, industry, exchange, market cap)
- Income statement (3-5 years historical + consensus estimates)
- Balance sheet (latest + 2-3 years historical)
- Cash flow statement (3-5 years historical)
- Key ratios (P/E, EV/EBITDA, EV/Revenue, P/B, ROE, ROIC)
- Analyst consensus (target price, rating, EPS estimates)
- Ownership structure (institutional, insider %)
- Earnings transcripts (latest 1-2 quarters) — via Aiera MCP if available
```

**Output from MCP**: Structured data that feeds directly into the Data Contract.

### Priority 2 — WebSearch (always runs, supplements MCP)

Run these queries regardless of MCP availability:

```
WebSearch: "{ticker} latest earnings results revenue EPS {current_quarter} {current_year}"
WebSearch: "{ticker} analyst consensus target price rating {current_year}"
WebSearch: "{ticker} market cap PE ratio EV/EBITDA valuation"
WebSearch: "{ticker} balance sheet debt cash {current_year}"
WebSearch: "{ticker} 52 week high low performance YTD"
```

**Purpose**: Cross-validate MCP data, fill gaps, and capture qualitative context (narrative, market sentiment) that APIs don't provide.

### Priority 3 — Yahoo Finance Script (optional fallback)

If Bash tool is available AND no MCP provider was found:

```
Bash: cd {plugin_root}/scripts && npx tsx yahoo-fetch.ts {ticker}
```

**Do NOT block on script failure.** This is purely an optional accelerator.

---

## Step 2: Build Data Contract

After Step 1, assemble the **Data Contract** — a single standardized file that ALL downstream skills and section-writers MUST reference. This is the single source of truth for quantitative data.

Save to: `Research/{ticker}/data_contract.md`

### Data Contract Format

```markdown
# Data Contract — {ticker}
Generated: {date}
Sources: {list of data sources used: MCP provider name, WebSearch, script}

## Company Profile
| Field | Value |
|-------|-------|
| Company Name | {name} |
| Ticker | {ticker} |
| Exchange | {exchange} |
| Sector / Industry | {sector} / {industry} |
| Market Cap | ${X}B |
| Enterprise Value | ${X}B |
| Current Price | ${X} (as of {date}) |
| 52-Week Range | ${low} - ${high} |
| Shares Outstanding | {X}M (basic) / {X}M (diluted) |
| Beta | {X} |

## Income Statement Summary
| Metric | FY-3A | FY-2A | FY-1A | FYE | FY+1E |
|--------|-------|-------|-------|-----|-------|
| Revenue ($M) | | | | | |
| Revenue Growth % | | | | | |
| Gross Profit ($M) | | | | | |
| Gross Margin % | | | | | |
| EBITDA ($M) | | | | | |
| EBITDA Margin % | | | | | |
| Operating Income ($M) | | | | | |
| Operating Margin % | | | | | |
| Net Income ($M) | | | | | |
| Net Margin % | | | | | |
| EPS (diluted) | | | | | |
| SBC ($M) | | | | | |
| SBC % of Revenue | | | | | |

## Balance Sheet Summary
| Metric | Latest |
|--------|--------|
| Total Assets ($M) | |
| Cash & Equivalents ($M) | |
| Total Debt ($M) | |
| Net Debt ($M) | |
| Shareholders' Equity ($M) | |
| Debt/Equity | |
| Net Debt/EBITDA | |
| Current Ratio | |
| Interest Coverage | |

## Cash Flow Summary
| Metric | FY-2A | FY-1A | FYE | FY+1E |
|--------|-------|-------|-----|-------|
| Operating Cash Flow ($M) | | | | |
| Capital Expenditures ($M) | | | | |
| Free Cash Flow ($M) | | | | |
| FCF Margin % | | | | |
| Dividends ($M) | | | | |
| Buybacks ($M) | | | | |

## Valuation Multiples
| Metric | Current | vs 5Y Avg | vs Peers |
|--------|---------|-----------|----------|
| P/E (TTM) | | | |
| P/E (FWD) | | | |
| EV/Revenue (TTM) | | | |
| EV/Revenue (FWD) | | | |
| EV/EBITDA (TTM) | | | |
| EV/EBITDA (FWD) | | | |
| P/B | | | |
| FCF Yield | | | |

## Analyst Consensus
| Field | Value |
|-------|-------|
| Rating | {Buy/Hold/Sell} |
| # of Analysts | |
| Target Price (Mean) | $ |
| Target Price (High) | $ |
| Target Price (Low) | $ |
| EPS Estimate (Current FY) | $ |
| EPS Estimate (Next FY) | $ |
| Revenue Estimate (Current FY) | $M |

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
- [List any fields that could not be populated]
- [List any conflicting data points and which source was chosen]
- [Flag stale data (>6 months old)]
```

### Data Contract Rules

1. **Every numeric field must cite its source** (MCP provider, specific WebSearch result, or SEC filing).
2. **If MCP and WebSearch give different numbers**, prefer MCP data (structured API) and note the discrepancy.
3. **Leave fields blank rather than guessing** — blank fields signal to downstream writers that data is unavailable.
4. **The Data Contract is immutable during a single research run** — once generated, all sections reference it; no section may override these numbers.

---

## Step 3: Qualitative Research (WebSearch)

**If `{mode}` = "quick"**: Skip this step. The Step 1/2 queries are sufficient.

**If `{mode}` = "full"**: Execute targeted searches to build qualitative context for all 21 sections.

### Research Queries by Section Group

**Group A — Strategy & Market (§1, §2, §5, §14)** — 6-8 queries
```
"{ticker} investment thesis bull bear case {current_year}"
"{ticker} TAM SAM addressable market size"
"{ticker} market share competitive position"
"{ticker} vs {competitor_1} vs {competitor_2}"
"{ticker} competitive moat switching costs barriers"
"{ticker} industry outlook growth drivers"
```

**Group B — Business Model (§3, §4, §7, §8, §9, §10)** — 4-6 queries
```
"{ticker} customer segments enterprise revenue breakdown"
"{ticker} product roadmap technology platform"
"{ticker} pricing strategy revenue model"
"{ticker} customer retention churn expansion"
```

**Group C — Operations & Risk (§6, §11, §16, §17, §18, §19)** — 4-6 queries
```
"{ticker} management CEO leadership execution"
"{ticker} supply chain operations manufacturing"
"{ticker} risk factors challenges headwinds"
"{ticker} M&A acquisitions strategy"
```

**Group D — AI & Data (§15)** — 1-2 queries
```
"{ticker} AI artificial intelligence strategy data"
```

**Group E — Valuation & Catalysts (§20, §21)** — 3-4 queries
```
"{ticker} valuation DCF fair value intrinsic"
"{ticker} peer comparison valuation multiples"
"{ticker} upcoming catalysts earnings date events"
```

**Total**: 18-26 targeted queries for full mode.

---

## Step 4: SEC EDGAR (US Market, full mode only)

**If `{mode}` = "quick"**: Skip.

If `{market}` = US, search for recent SEC filings:

```
WebSearch: "site:sec.gov {ticker} 10-K 10-Q {current_year}"
```

Note key filing dates and extract risk factors, segment disclosures, and accounting policies not available via MCP/WebSearch.

---

## Step 5: Coverage Validation (full mode only)

**If `{mode}` = "quick"**: Skip.

Build the Coverage Log and check against thresholds:

| Criterion | Threshold | Action if Fail |
|-----------|-----------|----------------|
| Unique sources | ≥ 30 | Continue searching until met or acknowledge gap |
| Source types covered | ≥ 4 of 6 types | Add targeted queries for missing types |
| MCP data populated | ≥ 80% of Data Contract fields | Note gaps in Data Quality Notes |
| Sources dated within 12 months | ≥ 50% | Prioritize recent sources |

**Source Types**: SEC Filings / Earnings-IR / Industry Report / Quality Media / Competitor Primary / Academic-Expert

### Coverage Log Format

| # | Title | Date | Source Type | Section(s) |
|---|-------|------|-------------|------------|
| 1 | ... | ... | ... | §X, §Y |

### Validation Behavior

- If any criterion fails, continue researching silently until it passes or exhaustive search is complete.
- If thresholds cannot be met, acknowledge gaps in the Coverage Validator output.
- Do NOT re-prompt the user.

---

## Output

Pass the following to the calling skill:

1. **Data Contract file** — saved to `Research/{ticker}/data_contract.md`
2. **Coverage Log** — source table (full mode) or abbreviated list (quick mode)
3. **Coverage Validator** — pass/fail for each criterion (full mode only)
4. **Key qualitative findings** — top 5-10 insights from WebSearch, organized by section relevance
