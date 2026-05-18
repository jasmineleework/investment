---
name: data-fetch
description: >
  Financial data collection for investment research.
  Detects runtime environment and uses the best available data sources:
  MCP tools (preferred), Python scripts (fallback), or WebSearch (last resort).
  Outputs a Data Contract file consumed by all downstream skills.
---

# Data Fetch

Collect and validate financial data for a given stock ticker. This skill is called by `stock-research` or `quick-check` and should not be invoked directly by the user.

## CRITICAL RULE: 禁止数据估计（No Approximation）

所有 **数值字段** 必须来自实时数据源（MCP 或脚本）。

**禁止**：
- "市场公开近似值"、"业界常见 ~22x"、"约莫 ~3.5x" 这类措辞
- 用训练数据中的记忆数值填表（cutoff 之外的数据必然过时）
- 跳过未抓取的字段而直接进入下游分析

**强制**：
- 每个数值（包括 peer）必须能追溯到 Data Contract 中的具体抓取记录
- Peer 列表中每家公司必须分别调用 `mcp__yfinance__*` 或 `yahoo_fetch.py <PEER_TICKER>` 抓取
- 真实抓不到的字段标 `N/A — 数据源不可得`，不写数字
- 输出 Data Contract 时，**每行附数据来源**（"yfinance MCP"、"yahoo_fetch.py"、"SEC EDGAR 10-Q 引用"）

任何含"~"、"约"、"approximately"、"市场公开近似"等措辞的 Data Contract 视为 **FAIL**，必须重新抓取。

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

Detect which data sources are available in the current runtime.

```
Check 1: Are MCP tools available?
  Look for tools matching: get_current_stock_price, get_financials, get_income_statement
  (These come from yfinance MCP and sec-edgar-mcp servers)

  If MCP tools found → Environment = "mcp" (best path)
  If MCP tools NOT found → Check 2

Check 2: Is Bash available?
  Bash: echo "ok"

  If Bash works → Environment = "claude-code" (script fallback)
  If Bash unavailable → Environment = "cowork" (WebSearch only)
```

**Route to the matching path:**
- `"mcp"` → **Path A** (MCP-first, scripts as fallback)
- `"claude-code"` → **Path A** (scripts as primary, skip MCP steps)
- `"cowork"` → **Path B** (WebSearch only)

---

## Path A: Claude Code Environment (MCP-first + script fallback)

### Three-Tier Data Strategy

Data is fetched in priority order. Each tier fills gaps left by previous tiers.

| Tier | Source | When to use |
|------|--------|-------------|
| Tier 1 | MCP tools | Always try first (if available) |
| Tier 2 | Python scripts | Fill gaps MCP can't cover, or when MCP unavailable |
| Tier 3 | WebSearch | Qualitative data + anything still missing |

---

### Step A1: Tier 1 — MCP Tools (preferred)

**Skip this step if Environment = "claude-code" (no MCP tools).**

#### A1a: Yahoo Finance MCP (price, financials, cash flow)

Call these tools in parallel:

| Tool | Parameters | Data it provides |
|------|-----------|-----------------|
| `get_current_stock_price` | `symbol: "{ticker}"` | Current price |
| `get_income_statement` | `symbol: "{ticker}", freq: "yearly"` | Revenue, net income, EBITDA, EPS (3-4 years) |
| `get_cashflow` | `symbol: "{ticker}", freq: "yearly"` | OCF, capex, FCF, dividends, buybacks |
| `get_historical_stock_prices` | `symbol: "{ticker}", period: "1y", interval: "1d"` | 1-year price history (for 52-week range) |
| `get_dividends` | `symbol: "{ticker}"` | Dividend history |
| `get_earning_dates` | `symbol: "{ticker}", limit: 4` | Upcoming/recent earnings dates |
| `get_news` | `symbol: "{ticker}"` | Recent news headlines |
| `get_recommendations` | `symbol: "{ticker}"` | Analyst rating distribution (strongBuy/buy/hold/sell/strongSell) + trend |

**Note**: Yahoo Finance MCP does NOT have balance sheet, quote-level fields (P/E, margins, beta), or company profile tools. These come from SEC MCP and scripts.

#### A1b: SEC EDGAR MCP (financials, balance sheet, key metrics)

For US stocks, call these tools in parallel:

| Tool | Parameters | Data it provides |
|------|-----------|-----------------|
| `get_financials` | `identifier: "{ticker}", statement_type: "all"` | Income, balance sheet, cash flow from latest SEC filing |
| `get_key_metrics` | `identifier: "{ticker}"` | Key XBRL metrics (revenue, net income, assets, debt, equity, etc.) |
| `get_company_info` | `identifier: "{ticker}"` | Company name, CIK, SIC, exchange, fiscal year end |
| `get_segment_data` | `identifier: "{ticker}"` | Revenue by segment/geography |
| `get_insider_summary` | `identifier: "{ticker}", days: 180` | Insider trading activity summary → maps to Data Contract "Insider Activity (180 days)" |

**For full mode**, also call:

| Tool | Parameters | Data it provides |
|------|-----------|-----------------|
| `get_recent_filings` | `identifier: "{ticker}", form_type: "10-K", days: 365` | Latest 10-K filing info |
| `compare_periods` | `identifier: "{ticker}", metric: "Revenues", start_year: {FY-3}, end_year: {FY}` | Revenue trend with CAGR |
| `analyze_insider_sentiment` | `identifier: "{ticker}", months: 6` | Insider buy/sell pattern analysis → maps to Data Contract "Insider Activity (180 days)" |

**SEC EDGAR is authoritative for**: balance sheet, historical financials, segment data, insider activity. Its numbers take priority over other sources when conflicts arise.

---

### Step A2: Tier 2 — Python Script Fallback

Use scripts to fill gaps that MCP tools cannot cover. Run even if MCP succeeded — scripts provide unique data.

#### A2a: Yahoo Finance script (quote-level fields MCP lacks)

```bash
cd {skill_root}/scripts
pip install -q -r requirements.txt
python3 yahoo_fetch.py {ticker}
```

**Purpose**: The yahoo_fetch.py script provides quote/info fields that no MCP tool covers:
- Valuation multiples: P/E, EV/EBITDA, EV/Revenue, P/B, FCF yield
- Margins: gross, operating, EBITDA, net
- Risk metrics: beta, 52-week range
- Profile: sector, industry, market cap, enterprise value, shares outstanding
- Analyst consensus: target price, ratings, EPS estimates
- Institutional ownership: major holders, top institutional holders (Tier 2 fallback for MCP gaps)

**If MCP provided all financials**: Still run this script for P/E, margins, beta, and analyst data.
**If MCP was unavailable**: This script becomes the primary data source for everything.
**If the script fails**: Note in Data Quality Notes, continue with remaining sources.

#### A2b: SEC EDGAR script (only if SEC MCP unavailable)

```bash
cd {skill_root}/scripts
python3 sec_edgar_fetch.py {ticker}
```

**Skip if SEC MCP already returned data.** Only run as fallback.

#### A2c: FRED script (macro data for WACC)

```bash
cd {skill_root}/scripts
python3 fred_fetch.py
```

No MCP exists for FRED data. This script is always needed for the risk-free rate.

**If script fails**: Use WebSearch:
```
WebSearch: "10 year US treasury yield today"
```

---

### Step A3: Tier 3 — WebSearch (qualitative + gap-filling)

Run targeted WebSearch queries to supplement structured data:

```
WebSearch: "{ticker} latest earnings results {current_quarter} {current_year}"
WebSearch: "{ticker} investment thesis bull bear case {current_year}"
WebSearch: "{ticker} competitive landscape market share"
```

**Purpose**: MCP and scripts give you numbers; WebSearch gives you narrative, context, and sentiment.

Also use WebSearch to fill any Data Contract fields still blank after Tiers 1-2 (e.g., forward estimates, peer comparisons).

-> **After Steps A1-A3, proceed to Step 2: Build Data Contract**

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

-> **After Steps B1-B4, proceed to Step 2: Build Data Contract**

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

**Note**: In Path A, some of these may already be covered by Step A3. Skip duplicates.

---

## Step 4: SEC EDGAR Filing Search (full mode only)

**If `{mode}` = "quick"**: Skip.

**If Environment = "mcp"**: SEC filing data was already fetched via MCP in Step A1b. Use WebSearch only for supplemental filing context:
```
WebSearch: "site:sec.gov {ticker} 10-K 10-Q {current_year}"
```

**If Environment = "claude-code" or "cowork"**: Only WebSearch is available:
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
| Unique sources | >= 30 | Continue searching until met or acknowledge gap |
| Source types covered | >= 4 of 6 types | Add targeted queries for missing types |
| Data Contract fields populated | >= 80% (mcp/claude-code) / >= 50% (cowork) | Note gaps in Data Quality Notes |
| Sources dated within 12 months | >= 50% | Prioritize recent sources |

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
