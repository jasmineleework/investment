---
name: data-fetch
description: >
  Financial data collection for investment research.
  Collects market data via WebSearch (primary) and optional Yahoo Finance
  script (accelerator), searches web sources, and retrieves SEC filings.
  Outputs structured data for use by other skills.
---

# Data Fetch

Collect and validate financial data for a given stock ticker. This skill is called by `stock-research` or `quick-check` and should not be invoked directly by the user.

## Inputs

- `{ticker}` — Stock ticker symbol (e.g., AAPL)
- `{market}` — Market identifier (default: US)
- `{mode}` — `"full"` (default, for /research) or `"quick"` (for /quick-check)

## Outputs

1. **Structured financial data** (from WebSearch + optional script)
2. **Web source list** (from WebSearch; full mode targets 60+ unique sources)
3. **Coverage Log** for validation (full mode only)

---

## Step 1: Core Financial Data

### Primary Path — WebSearch (always runs)

Run these queries to collect key financial metrics:

```
WebSearch: "{ticker} stock price market cap PE EV/EBITDA revenue growth {current_year}"
WebSearch: "{ticker} earnings revenue gross margin operating margin FCF"
WebSearch: "{ticker} balance sheet debt cash shares outstanding"
WebSearch: "{ticker} analyst target price consensus rating"
WebSearch: "{ticker} 52 week high low stock performance"
```

Extract and organize into a structured summary:

| Data Category | Fields |
|---------------|--------|
| **Quote** | price, marketCap, PE (TTM + forward), PB, EV/EBITDA, EV/Revenue, dividendYield, 52wHigh/Low |
| **Financials** | revenue, grossProfit, grossMargin, operatingMargin, profitMargin, netIncome, EPS, revenue growth |
| **Balance Sheet** | totalAssets, totalDebt, cash, shareholdersEquity, debtToEquity, currentRatio |
| **Cash Flow** | operatingCF, capex, FCF, SBC |
| **Analyst** | consensus rating, target price (mean/high/low), number of analysts |

### Optional Accelerator — Yahoo Finance Script

If Bash tool is available AND the script environment is set up:

```
Bash: cd {plugin_root}/scripts && npx tsx yahoo-fetch.ts {ticker}
```

This returns structured JSON that supplements WebSearch data. **If the script fails for any reason (missing dependencies, sandbox restrictions, network errors), continue without it.** All required data can be obtained via WebSearch.

**Important**: Do NOT block on script failure. The WebSearch path above is sufficient.

---

## Step 2: WebSearch Information Sources

**If `{mode}` = "quick"**: Skip this step. The Step 1 queries plus 3-5 additional targeted queries (in quick-check command) are sufficient.

**If `{mode}` = "full"**: Execute targeted searches to build the Coverage Log. Organize queries by the 21-section structure of the investment memo.

### Phase 1 — Critical Sections (3-5 queries each)

**§1 Thesis Framework**
- `"{ticker} investment thesis {current_year}"`
- `"{ticker} bull case bear case"`
- `"{ticker} variant perception catalyst"`

**§2 Market Structure & Size**
- `"{ticker} TAM SAM market size"`
- `"{ticker} industry growth rate outlook"`
- `"{ticker} market share penetration"`

**§12 Financial Condition**
- `"{ticker} earnings revenue growth margin"`
- `"{ticker} Rule of 40 FCF margin"`
- `"{ticker} billings RPO backlog"`

**§13 Capital Structure**
- `"{ticker} debt maturity leverage ratio"`
- `"{ticker} capital allocation buyback dividend"`

**§20 Valuation Framework**
- `"{ticker} valuation EV/Revenue EV/EBITDA PE"`
- `"{ticker} DCF fair value target price"`
- `"{ticker} peer comparison comps"`

**§21 Scenarios & Catalysts**
- `"{ticker} upcoming catalysts earnings date"`
- `"{ticker} risks headwinds challenges {current_year}"`

### Phase 2 — Remaining Sections (1-2 queries each)

**§3 Customer**: `"{ticker} customer segments enterprise SMB"`
**§4 Product**: `"{ticker} product roadmap new features"`
**§5 Competition**: `"{ticker} vs competitors market share"`
**§6 Ecosystem**: `"{ticker} platform ecosystem developers API"`
**§7 GTM**: `"{ticker} go-to-market sales strategy channel"`
**§8 Retention**: `"{ticker} net dollar retention churn NRR"`
**§9 Monetization**: `"{ticker} revenue model pricing subscription"`
**§10 Pricing**: `"{ticker} pricing power elasticity ARPU"`
**§11 Unit Economics**: `"{ticker} CAC LTV payback period"`
**§14 Moat**: `"{ticker} competitive moat switching costs"`
**§15 Data & AI**: `"{ticker} AI strategy data advantage"`
**§16 Execution**: `"{ticker} management team leadership CEO"`
**§17 Supply Chain**: `"{ticker} supply chain operations risk"`
**§18 Risk**: `"{ticker} risk factors 10-K SEC filing"`
**§19 M&A**: `"{ticker} acquisitions M&A strategy"`

### Phase 3 — Source Diversification

After initial queries, check Coverage Log diversity. If needed, add targeted queries:
- Competitor primary sources: `"{competitor_name} vs {ticker}"`
- Academic/expert: `"{ticker} industry expert analysis academic paper"`
- Quality media: `"{ticker} Bloomberg OR WSJ OR FT OR Reuters analysis"`

---

## Step 3: SEC EDGAR (US Market)

**If `{mode}` = "quick"**: Skip this step.

If `{market}` = US, fetch recent SEC filings via WebFetch:

```
WebFetch: https://efts.sec.gov/LATEST/search-index?q="{ticker}"&dateRange=custom&startdt=2024-01-01&enddt=2026-12-31&forms=10-K,10-Q,8-K
```

Extract key filings:
- Most recent 10-K (annual report)
- Most recent 10-Q (quarterly report)
- Recent 8-K filings (material events)

---

## Step 4: FRED Macro Data (US Market)

**If `{mode}` = "quick"**: Skip this step.

If `{market}` = US, fetch key macro indicators via WebFetch:

```
WebFetch: https://fred.stlouisfed.org/series/FEDFUNDS  (Fed Funds Rate)
WebFetch: https://fred.stlouisfed.org/series/CPIAUCSL  (CPI)
WebFetch: https://fred.stlouisfed.org/series/GDP        (GDP)
```

These provide context for §13 Capital Structure (WACC inputs) and §18 Risk (macro risks).

---

## Step 5: Coverage Validation

**If `{mode}` = "quick"**: Skip this step.

Build the Coverage Log and check against thresholds:

| Criterion | Threshold | Action if Fail |
|-----------|-----------|----------------|
| Unique sources | ≥ 60 | Continue searching until met or acknowledge gap |
| Quality media sources | ≥ 10 | Add Bloomberg/WSJ/FT/Reuters targeted queries |
| Competitor primary sources | ≥ 5 | Search competitor names directly |
| Academic/expert sources | ≥ 5 | Search academic databases, expert commentary |
| Sources dated within 24 months | ≥ 60% | Prioritize recent sources in queries |
| Sources from any single domain | ≤ 10% | Diversify search domains |

### Coverage Log Format

| # | Title | Link | Date | Source Type | Region | Domain | Section | Notes | Time-Sensitive |
|---|-------|------|------|-------------|--------|--------|---------|-------|----------------|

**Source Types**: SEC Filings / Earnings-IR / Industry Report / Quality Media / Competitor Primary / Academic-Expert

### Uniqueness Calculation

Count unique sources by **Domain + Document Title** combination. Multiple pages from the same article count as one source.

### Time-Sensitivity Protocol

- Mark each time-sensitive metric (price, earnings, guidance, macro data) as **"Yes"** in the Time-Sensitive column.
- Print its date; update if newer data exists.
- If retaining older data, state rationale for retention.

### Validation Behavior

- If any validator criterion is **"Fail"**, continue researching silently until all pass.
- Do NOT re-prompt the user during validation — resolve gaps autonomously.
- If 60-source threshold cannot be met after exhaustive search, acknowledge the gap in the Coverage Validator output and append a Research Methodology Note stating which criteria fell short and why.

---

## Output

Pass the following to the calling skill (stock-research or quick-check):

1. **Financial data summary** — structured metrics from WebSearch (+ script if available)
2. **Coverage Log** — full source table (full mode) or abbreviated list (quick mode)
3. **Coverage Validator** — pass/fail for each criterion (full mode only)
4. **Key findings summary** — top 5-10 most important data points discovered during research, organized by section relevance
