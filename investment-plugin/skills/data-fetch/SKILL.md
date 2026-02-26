---
name: data-fetch
description: >
  Financial data collection for investment research.
  Detects runtime environment and uses the best available data sources:
  Claude Code (direct API access) or Cowork (WebSearch only).
  Outputs a Data Contract file consumed by all downstream skills.
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

## Step 0: Environment Detection

Detect the runtime environment to determine which data sources are available.

```
Test: Run a simple Bash command to check network access
  Bash: curl -s --max-time 5 -o /dev/null -w "%{http_code}" https://query1.finance.yahoo.com

  If HTTP 200 → Environment = "claude-code" (direct API access)
  If HTTP 403 or timeout → Environment = "cowork" (sandbox restricted)
  If Bash unavailable → Environment = "cowork"
```

**Then follow the matching path below.**

---

## Path A: Claude Code Environment (direct API access)

### Step A1: Yahoo Finance API (PRIMARY data source)

Install and run the Yahoo Finance data fetcher:

```bash
cd {skill_root}/scripts
pip install -q -r requirements.txt
python3 yahoo_fetch.py {ticker}
```

If the script exists and works, it will output structured JSON. Parse it into the Data Contract.

**If the script fails**: Note the failure in Data Quality Notes and continue with other sources.

**Yahoo Finance provides**:
- Company profile (name, sector, industry, exchange, market cap)
- Stock quote (price, 52-week range, volume, beta)
- Income statement (3-5 years: revenue, gross profit, EBITDA, net income, EPS)
- Balance sheet (assets, debt, cash, equity, ratios)
- Cash flow statement (OCF, capex, FCF, dividends, buybacks)
- Valuation multiples (P/E, EV/EBITDA, EV/Revenue, P/B, FCF yield)
- Analyst consensus (target price, rating, EPS estimates)
- Institutional ownership %

### Step A2: SEC EDGAR API (US market, structured XBRL data)

For US stocks, fetch structured financial data from SEC EDGAR:

```bash
cd {skill_root}/scripts
python3 sec_edgar_fetch.py {ticker}
```

The script resolves the CIK, downloads XBRL company facts to `/tmp/{ticker}_sec_facts.json`, and lists key XBRL fields in its comments.

**Purpose**: Cross-validate Yahoo Finance numbers with official SEC filings. SEC data is authoritative for historical financials.

**If fetch fails**: Skip SEC step, rely on Yahoo Finance alone. Note in Data Quality Notes.

### Step A3: FRED API (macro data for WACC)

```bash
cd {skill_root}/scripts
python3 fred_fetch.py          # defaults to DGS10 (10-Year US Treasury)
# or: python3 fred_fetch.py <SERIES_ID> [FRED_API_KEY]
```

The script tries the JSON API first (if API key is available), then falls back to the CSV endpoint. Compatible with both macOS and Linux.

**If the script fails**: Use WebSearch to find the latest 10Y Treasury yield:
```
WebSearch: "10 year US treasury yield today"
```

### Step A4: WebSearch (qualitative supplement)

Run targeted WebSearch queries to supplement API data with qualitative context:

```
WebSearch: "{ticker} latest earnings results {current_quarter} {current_year}"
WebSearch: "{ticker} investment thesis bull bear case {current_year}"
WebSearch: "{ticker} competitive landscape market share"
```

**Purpose**: APIs give you numbers; WebSearch gives you narrative, context, and sentiment.

→ **After Steps A1-A4, proceed to Step 2: Build Data Contract**

---

## Path B: Cowork Environment (WebSearch only)

All direct HTTP requests are blocked by egress proxy. WebSearch is the only data source.

### Step B1: Core Financial Data Queries

Run these queries to populate the Data Contract:

```
WebSearch: "{ticker} stock price market cap PE ratio EV/EBITDA {current_year}"
WebSearch: "{ticker} revenue net income EPS annual results FY{last_year} FY{current_year}"
WebSearch: "{ticker} gross margin operating margin EBITDA margin"
WebSearch: "{ticker} balance sheet total debt cash net debt {current_year}"
WebSearch: "{ticker} free cash flow capital expenditure operating cash flow"
WebSearch: "{ticker} 52 week high low beta shares outstanding"
WebSearch: "{ticker} analyst consensus target price rating {current_year}"
WebSearch: "{ticker} EPS estimate revenue estimate next quarter next year"
WebSearch: "{ticker} dividend yield buyback shareholder return"
```

### Step B2: WACC Inputs

```
WebSearch: "10 year US treasury yield today {current_year}"
WebSearch: "{ticker} beta cost of equity WACC"
```

### Step B3: Qualitative Context (full mode only)

**If `{mode}` = "quick"**: Skip.

```
WebSearch: "{ticker} investment thesis bull bear case {current_year}"
WebSearch: "{ticker} TAM SAM addressable market size growth"
WebSearch: "{ticker} competitive moat vs competitors"
WebSearch: "{ticker} customer segments revenue breakdown"
WebSearch: "{ticker} product roadmap technology strategy"
WebSearch: "{ticker} management CEO execution track record"
WebSearch: "{ticker} supply chain operations risk"
WebSearch: "{ticker} M&A acquisitions"
WebSearch: "{ticker} AI strategy data advantage"
WebSearch: "{ticker} upcoming catalysts earnings date events"
WebSearch: "{ticker} risk factors headwinds challenges"
WebSearch: "site:sec.gov {ticker} 10-K 10-Q {current_year}"
```

### Step B4: Peer Comparison Data

```
WebSearch: "{ticker} vs {peer_1} vs {peer_2} valuation comparison"
WebSearch: "{ticker} industry peers financial comparison"
```

**Total queries**: 11-13 (quick mode), 24-28 (full mode)

→ **After Steps B1-B4, proceed to Step 2: Build Data Contract**

---

## Step 2: Build Data Contract

After Step 1 (Path A or B), assemble the **Data Contract** — a single standardized file that ALL downstream skills and section-writers MUST reference. This is the single source of truth for quantitative data.

Save to: `Research/{ticker}/data_contract.md`

Use the template and rules defined in `references/data_contract.md` to build the contract instance. Save the filled instance to `Research/{ticker}/data_contract.md`.

---

## Step 3: Qualitative Research (WebSearch)

**If `{mode}` = "quick"**: Skip this step.

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

**Note**: In Claude Code environment (Path A), some of these may already be covered by Step A4. Skip duplicates.

---

## Step 4: SEC EDGAR Filing Search (full mode only)

**If `{mode}` = "quick"**: Skip.

**Claude Code**: Already fetched structured XBRL data in Step A2. This step adds filing-level context:
```
WebSearch: "site:sec.gov {ticker} 10-K 10-Q {current_year}"
```

**Cowork**: Only WebSearch is available:
```
WebSearch: "site:sec.gov {ticker} 10-K 10-Q {current_year}"
```

Note key filing dates and extract risk factors, segment disclosures, and accounting policies.

---

## Step 5: Coverage Validation (full mode only)

**If `{mode}` = "quick"**: Skip.

Build the Coverage Log and check against thresholds:

| Criterion | Threshold | Action if Fail |
|-----------|-----------|----------------|
| Unique sources | ≥ 30 | Continue searching until met or acknowledge gap |
| Source types covered | ≥ 4 of 6 types | Add targeted queries for missing types |
| Data Contract fields populated | ≥ 80% (claude-code) / ≥ 50% (cowork) | Note gaps in Data Quality Notes |
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
