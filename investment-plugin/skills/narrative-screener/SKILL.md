---
name: narrative-screener
description: >
  Narrative-driven stock discovery and screening system.
  Takes an investment narrative as input, decomposes it into a structured
  beneficiary chain, discovers 10-20 candidates via multi-source search,
  filters to 3-5 via scoring funnel, then runs full quick-check evaluation
  with smart-money signals. Outputs a ranked valuation-gap report.
  Called by the /narrative-screen command.
---

# Narrative Screener

From an investment narrative to ranked valuation-gap candidates. Four-phase funnel: Decompose → Discover → Filter → Evaluate.

## Inputs

- `{narrative}` — User's investment narrative text (e.g., "Data center power demand doubling")
- `{output_language}` — Detected from user's input (Chinese / English)

## Outputs

All files saved to `Research/narratives/{date}_{narrative_slug}/`:

| File | Phase | Content |
|------|-------|---------|
| `narrative-map.md` | 1 | Structured narrative decomposition |
| `discovery-pool.md` | 2 | Broad candidate pool (10-20 tickers) |
| `shortlist-ranking.md` | 3 | Scored ranking + elimination log |
| `screening-report.md` | 4 | Final report with valuation-gap ranking |
| `candidates/{TICKER}/` | 4 | Per-ticker evaluation files |

---

## Step 0: Input Parsing & Setup

### Language Detection

Detect output language from user's narrative input:
- Chinese input → `{output_language}` = Chinese
- English input → `{output_language}` = English
- Other → match the user's language

**This applies to ALL output files.** Only financial terms, ticker symbols, and proper nouns remain in English.

### Slug Generation

Convert the narrative to a kebab-case slug for the output directory:
- "数据中心电力需求翻倍" → `data-center-power-demand`
- "GLP-1 weight loss drug revolution" → `glp1-weight-loss`

### Output Path

```
{workspace}/Research/narratives/{YYYY-MM-DD}_{narrative_slug}/
```

Create this directory before proceeding.

### Load Market Config

Read `references/markets/us.md` for threshold parameters:
- `{HURDLE_TR_%}`, `{MOS_%}`, `{SKEW_X}`, `{QUALITY_PASS}`, `{QUALITY_SELL}`

These are used in Phase 4 when calling `decision-rules`.

---

## Phase 1: Narrative Decomposition (~3 min)

**Goal**: Transform the user's free-text narrative into a structured analytical framework.

### Step 1.1: LLM Reasoning

Decompose the narrative into 6 components:

```markdown
## Narrative: {user's narrative text}

### Core Drivers
- Driver 1: [description] → Quantifiable indicator: [...]
- Driver 2: [description] → Quantifiable indicator: [...]

### Beneficiary Chain
L1 (Direct): [company types/industries] — Revenue directly from this trend
L2 (Indirect): [company types/industries] — Benefits from L1 growth
L3 (Derivative): [company types/industries] — Further transmission chain

### Key Assumptions
- Assumption 1: If [condition], then [outcome] — Verification metric: [...]
- Assumption 2: If [condition], then [outcome] — Verification metric: [...]

### Time Horizon
- Short-term (0-6mo): [expected developments]
- Medium-term (6-18mo): [expected developments]
- Long-term (18-36mo): [expected developments]

### Theme Lifecycle Stage
[ ] Nascent — few observers, no theme ETFs
[ ] Growth — rising attention, capital inflows
[ ] Mature — widely recognized, valuations may be rich
[ ] Crowded — overcrowded, watch for pullback
Basis: [news frequency / ETF AUM / valuation levels / analyst coverage density]

### Counter-Narrative
- Under what conditions does this narrative fail?
- Who are the losers? (reverse beneficiaries)
- Crowding risk assessment
```

### Step 1.2: Web Validation

Run 2-3 WebSearch queries to ground the decomposition:

```
WebSearch: "{narrative keywords} market size TAM growth forecast"
WebSearch: "{narrative keywords} ETF holdings thematic fund"
WebSearch: "{narrative keywords} investment theme analysis {current_year}"
```

Update the narrative map with data points from search results (market size, growth rates, ETF references).

### Output

Save to `narrative-map.md` in the output directory.

---

## Phase 2: Broad Discovery (~5 min)

**Goal**: Cast a wide net to find 10-20 candidate stocks across the beneficiary chain.

### Step 2.1: Multi-Source Parallel Discovery

Run these data sources **in parallel**:

#### WebSearch (4-6 queries)

```
WebSearch: "{narrative keywords} stocks beneficiaries {current_year}"
WebSearch: "{narrative keywords} ETF top holdings"
WebSearch: "{narrative keywords} companies revenue exposure"
WebSearch: "{L1 industry} leading companies market share"
WebSearch: "{L2 industry} growth companies investment"
WebSearch: "{narrative keywords} emerging opportunities small mid cap"
```

#### SEC EDGAR

```
search_companies(query="{L1 industry keyword}")
search_companies(query="{L2 industry keyword}")
```

#### yfinance

For any ticker surfaced by WebSearch or SEC, fetch market cap:
```
get_current_stock_price(symbol="{ticker}")
```

### Step 2.2: Filtering Criteria

Apply hard filters to the raw candidate list:
- **Exchange**: NYSE or NASDAQ only (ADRs included)
- **Market Cap**: > $500M (filter out micro-caps)
- **Relevance**: Must have a plausible link to the narrative

### Step 2.3: Organize by Beneficiary Chain

Group candidates by L1/L2/L3 and attach for each:
- 1-sentence thesis: why this company benefits
- Market cap
- Beneficiary tier (L1/L2/L3)

### Output

Save to `discovery-pool.md`:

```markdown
# Discovery Pool: {narrative}
**Date**: {date} | **Candidates**: {N}

## L1 — Direct Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|
| 1 | XXX | ... | $XXB | ... |

## L2 — Indirect Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|

## L3 — Derivative Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|
```

Target: 10-20 candidates. If fewer than 8, expand search scope (broaden L2/L3, lower market cap threshold to $300M). If more than 25, tighten relevance or raise market cap floor.

---

## Phase 3: Shortlist Funnel (~5 min)

**Goal**: Score each candidate across 4 dimensions and select Top 3-5 for full evaluation.

### Step 3.1: Lightweight Data Collection (per candidate, parallel)

For each candidate in the discovery pool, fetch:

#### yfinance (parallel per ticker)

```
get_income_statement(symbol="{ticker}", freq="yearly")
get_cashflow(symbol="{ticker}", freq="yearly")
get_recommendations(symbol="{ticker}")
get_current_stock_price(symbol="{ticker}")
```

#### SEC EDGAR (parallel per ticker)

```
get_insider_summary(identifier="{ticker}", days=180)
get_company_info(identifier="{ticker}")
```

#### WebSearch (1 query per ticker)

```
WebSearch: "{ticker} {company_name} revenue exposure {narrative keywords}"
```

### Step 3.2: Four-Dimension Scoring

Score each candidate on 4 dimensions. Read scoring criteria from reference files.

#### 1. Narrative Fit Score (0-100)

**Read**: `references/narrative-fit-scoring.md`

Evaluate: revenue exposure, transmission certainty, management intent, differentiation.

```
NarrativeFit = (RevenueExposure×0.35 + TransmissionCertainty×0.25 + MgmtIntent×0.20 + Differentiation×0.20) × 20
```

#### 2. Smart Money Signal (0-100)

**Read**: `references/smart-money-signals.md`

Evaluate: analyst ratings, insider transactions, institutional positioning.

```
SmartMoney = Analyst×0.30 + Insider×0.40 + Institutional×0.30
```

**Phase 3 uses the "Quick" version** — lightweight data only (insider summary, recommendations, 1 WebSearch for institutional).

#### 3. Fundamental Quick Score (0-100)

Calculate from yfinance data:

**Calculation definitions** (using `get_income_statement` + `get_cashflow` + `get_current_stock_price`):
- **Revenue Growth (YoY)**: (Latest FY Revenue - Prior FY Revenue) / Prior FY Revenue
- **Gross Margin**: (Revenue - Cost of Revenue) / Revenue from latest FY
- **FCF Yield**: (Operating Cash Flow - Capital Expenditure) / Market Cap

| Sub-metric | Weight | Scoring |
|-----------|--------|---------|
| Revenue Growth (YoY) | 40% | >30%→100, 20-30%→80, 10-20%→60, 0-10%→40, <0%→20 |
| Gross Margin | 30% | >60%→100, 50-60%→80, 40-50%→60, 30-40%→40, <30%→20 |
| FCF Yield | 30% | >8%→100, 5-8%→80, 3-5%→60, 0-3%→40, <0%→20 |

```
FundamentalQuick = RevGrowth×0.40 + GrossMargin×0.30 + FCFYield×0.30
```

#### 4. Valuation Discount (0-100)

Estimate relative cheapness using available Phase 3 data + 1 WebSearch:

**Data sources**:
- Current P/E: derive from income statement (net income / shares) vs current price
- Historical P/E median: WebSearch `"{ticker} historical PE ratio 5 year"` (from Phase 3 per-ticker query)
- Peer EV/Revenue: compare against other candidates in the same L-tier from discovery pool

| Sub-metric | Weight | Scoring |
|-----------|--------|---------|
| P/E vs 5yr median | 50% | >30% discount→100, 20-30%→80, 10-20%→60, 0-10%→40, premium→20 |
| EV/Revenue vs peers | 50% | >30% discount→100, 20-30%→80, 10-20%→60, 0-10%→40, premium→20 |

If historical P/E or peer EV/Revenue data is unavailable, use a single metric at 100% weight.

```
ValuationDiscount = (PEDiscount×0.50 + EVRevDiscount×0.50)
```

### Step 3.3: Composite Ranking

```
Shortlist Score = NarrativeFit×0.35 + FundamentalQuick×0.25 + SmartMoney×0.20 + ValuationDiscount×0.20
```

### Step 3.4: Elimination Rules

Remove candidates before ranking if ANY of the following apply:
- **NarrativeFit < 60** — insufficient narrative connection
- **FundamentalQuick < 40** — fundamental weakness (low growth, weak margins, or negative FCF)
- **ValuationDiscount < 30** — no valuation margin of safety (premium pricing fully reflects theme)
- **Smart Money Red Flag** — any red flag per `smart-money-signals.md` (CEO/CFO non-plan selling, analyst mass downgrade, multi-fund exodus)

### Step 3.5: Select Top 3-5

Take the top 3-5 candidates by Shortlist Score after eliminations.

If fewer than 3 survive elimination: relax NarrativeFit threshold to 50, note the relaxation in output.

### Output

Save to `shortlist-ranking.md`:

```markdown
# Shortlist Ranking: {narrative}
**Date**: {date} | **Pool**: {N} → **Shortlisted**: {M}

## Ranking

| Rank | Ticker | Company | NarrFit | Fund | SmartMoney | ValDiscount | **Score** | Status |
|------|--------|---------|---------|------|------------|-------------|-----------|--------|
| 1 | XXX | ... | 85 | 72 | 78 | 68 | **77.2** | → Phase 4 |
| 2 | YYY | ... | 78 | 65 | 82 | 55 | **71.4** | → Phase 4 |
| ... | | | | | | | | |

## Eliminated

| Ticker | Company | Reason |
|--------|---------|--------|
| AAA | ... | NarrativeFit 48 — revenue exposure < 5% |
| BBB | ... | Red Flag: CEO sold $2M non-plan in 60 days |
```

---

## Phase 4: Full Evaluation (~10-15 min)

**Goal**: Run complete quick-check + smart money deep dive on each shortlisted candidate. Produce the final screening report.

**IMPORTANT**: Process candidates **sequentially** (not parallel) to avoid tool call overload.

### Step 4.1: Per-Candidate Evaluation

For each shortlisted ticker, execute:

#### 4.1a: Data Fetch

Call `skills/data-fetch/SKILL.md` with:
- `{ticker}` = candidate ticker
- `{mode}` = "quick"
- `{market}` = "US"

Output: `Research/{TICKER}/data_contract.md` (default data-fetch path)

After completion, copy the data_contract.md to the narrative output directory:
`candidates/{TICKER}/data_contract.md`

#### 4.1b: Quality Scorecard

Call `skills/quality-scorecard/SKILL.md` using the data contract from 4.1a.

**Adaptation for narrative-screener context**: Since there are no 21-section chapters, score conservatively:
- **Market** and **Financial Quality**: Score normally from data_contract + WebSearch context
- **Moat**, **Execution**, **Unit Economics**: If insufficient evidence, default to 3/5 with note "Limited data — conservative estimate"

Output: `candidates/{TICKER}/quality_score.md`

#### 4.1c: Valuation (Simplified)

Call `skills/valuation/SKILL.md` with data from the data contract.

**Simplification**:
- Peer list: draw from candidates in the same L-tier from the discovery pool
- Run all 3 methods (Comps, DCF, Reverse DCF) but accept wider confidence intervals

Output: `candidates/{TICKER}/valuation.md`

#### 4.1c½: Mini-Scenario Construction

Construct bear/base/bull scenarios from valuation output + narrative context. This bridges the gap between valuation (which outputs a fair value range) and decision-rules (which requires scenario probabilities, returns, and catalysts).

**Return Derivation** (mechanical — from valuation output):

```
Bull Return = (Fair Value High / Current Price) - 1
Base Return = (Fair Value Mid / Current Price) - 1
Bear Return = (Fair Value Low / Current Price) - 1
```

**Bear Case Floor** (from decision-rules guardrails):
- If beta ≥ 1.0 AND Bear Return > -20%: override Bear Return = -20%, adjust Fair Value Low = Current Price × 0.80
- Bear thesis = Phase 1 Counter-Narrative (already constructed)

**Probability Assignment** (based on Phase 1 Theme Lifecycle Stage):

| Lifecycle Stage | P(Bear) | P(Base) | P(Bull) |
|----------------|---------|---------|---------|
| Nascent | 30% | 40% | 30% |
| Growth | 20% | 45% | 35% |
| Mature | 25% | 50% | 25% |
| Crowded | 35% | 45% | 20% |

**E[TR] Calculation**:
```
E[TR] = P(Bull) × Bull Return + P(Base) × Base Return + P(Bear) × Bear Return
```

**Catalyst Extraction**:
1. Primary: next earnings date from data contract (Earning Dates fields)
2. Secondary: first dated event from Phase 1 Time Horizon → Short-term section
3. Each catalyst must state: specific date, expected impact (quantified), mechanism

Output: scenario parameters passed directly to Step 4.1d (not a separate file).

#### 4.1d: Decision Rules

Call `skills/decision-rules/SKILL.md` with:
- Valuation outputs from 4.1c (Fair Value Range, Buy/Trim Zones)
- Scenario parameters from 4.1c½ (Bear/Base/Bull returns, probabilities, E[TR], catalysts)
- Quality Score from 4.1b
- Thresholds from `references/markets/us.md`

Output: `candidates/{TICKER}/decision.md`

#### 4.1e: Smart Money Deep Dive

This is the **Phase 4 "Deep" version** of smart money analysis. Read `references/smart-money-signals.md` for the deep-mode tool chain.

**Data collection**:

```
SEC: analyze_form4_transactions(identifier="{ticker}", days=90)
SEC: analyze_insider_sentiment(identifier="{ticker}", months=6)
yfinance: get_recommendations(symbol="{ticker}")
WebSearch: "{ticker} institutional ownership 13F changes {current_quarter} {current_year}"
WebSearch: "{ticker} hedge fund positions top holders {current_year}"
```

**Produce Smart Money assessment**:
- Analyst Signal score (0-100)
- Insider Signal score (0-100)
- Institutional Signal score (0-100)
- Composite Smart Money Score = Analyst×0.30 + Insider×0.40 + Institutional×0.30
- Red flags (if any)
- Notable highlights (e.g., "CFO bought $500K on open market")

Output: `candidates/{TICKER}/smart_money.md`

### Step 4.2: Compile Final Report

After all candidates are evaluated, compile `screening-report.md`.

#### Report Structure

```markdown
# Narrative Screening Report: {narrative}
**Date**: {date} | **Theme Lifecycle**: {stage} | **Pool**: {N} → **Shortlisted**: {M}

---

## Narrative Map
[Include Phase 1 narrative decomposition from narrative-map.md]

---

## Valuation Gap Ranking

| Rank | Ticker | Company | Quality | MOS% | 4-Gate | Smart Money | Rating | Gap Index |
|------|--------|---------|---------|------|--------|-------------|--------|-----------|
| 1 | XXX | ... | 78/100 | 32% | 4/4 | 82/100 | **Buy** | {stars} |
| 2 | YYY | ... | 71/100 | 28% | 3/4 | 75/100 | **Hold** | {stars} |

**Gap Index** = Weighted composite: MOS% (highest weight) + Quality + Smart Money confirmation

Gap Index star rating:
- 5 stars: MOS ≥ 30% + Quality ≥ 75 + SmartMoney ≥ 75 + 4/4 Gates
- 4 stars: MOS ≥ 25% + Quality ≥ 70 + SmartMoney ≥ 65
- 3 stars: MOS ≥ 20% + Quality ≥ 65 + SmartMoney ≥ 55
- 2 stars: MOS ≥ 15% + Quality ≥ 60
- 1 star: MOS < 15% or Quality < 60

---

## Shortlisted Candidates

### #1 {TICKER} — {Company Name} {gap_badge}

**Narrative Benefit Path**:
{narrative} → [specific transmission mechanism] → {X}% revenue directly benefits

**Quick-Check Results**:

| Gate | Metric | Value | Threshold | Result |
|------|--------|-------|-----------|--------|
| 1. Expected Return | E[TR] | XX% | ≥ 30% | pass/fail |
| 2. Margin of Safety | MOS | XX% | ≥ 25% | pass/fail |
| 3. Skew | E[TR]/|Bear| | X.X× | ≥ 1.7× | pass/fail |
| 4. Catalyst | {name} | {date} | Within 24mo | pass/fail |
| Quality | Score | XX/100 | ≥ 70 | pass/fail |

**Rating: {Buy/Hold/Await/Sell}** | Fair Value: ${XX} | Current: ${XX}

**Smart Money Signals**:
- Analyst: {X}% Buy, consensus target ${XX} (upside {X}%)
- Insider: 90-day activity: {summary}
- Institutional: {summary}

**Key Bull Points**: 1-2 items
**Key Risks**: 1-2 items
**Next Step**: → `/research {TICKER}` for full deep dive

---

[Repeat for each shortlisted candidate]

---

## Eliminated Candidates

| Ticker | Company | L-Tier | Elimination Reason |
|--------|---------|--------|-------------------|
| AAA | ... | L1 | NarrativeFit 52 — revenue exposure insufficient |
| BBB | ... | L2 | Red Flag: insider large sale |
| CCC | ... | L1 | Valuation fully priced-in (P/S 95th pctl) |

---

## Methodology Notes

- **Narrative Fit**: Scored per `narrative-fit-scoring.md` (revenue exposure × 0.35 + transmission certainty × 0.25 + mgmt intent × 0.20 + differentiation × 0.20)
- **Smart Money**: Scored per `smart-money-signals.md` (analyst × 0.30 + insider × 0.40 + institutional × 0.30)
- **Quality/Valuation/Decision**: Standard skill chain (data-fetch → quality-scorecard → valuation → decision-rules)
- **Thresholds**: Per `references/markets/us.md`
```

### Output

Save to `screening-report.md` in the output directory.

---

## Edge Cases

### Too Few Candidates (< 5 in discovery pool)
- Broaden L2/L3 search scope
- Lower market cap threshold to $300M
- Add 2-3 more WebSearch queries with alternative keywords
- If still < 5 after expansion, proceed with what's available and note "limited candidate universe" in report

### No Insider Transaction Data
- SEC EDGAR may return empty for some tickers
- Score insider dimension as 50/100 (neutral) and note "No recent insider transactions"
- Do not penalize or reward — absence of data is not a signal

### SEC MCP Timeout or Error
- Skip SEC-dependent data for that ticker
- Use yfinance + WebSearch as fallback
- Note in Data Quality section of the candidate's evaluation

### All Candidates Eliminated in Phase 3
- Relax NarrativeFit threshold from 60 to 50
- If still none survive, report "No candidates meet screening criteria" with explanation
- Suggest: alternative narrative framing, broader scope, or different time horizon

### Narrative Too Broad or Too Narrow
- Too broad (e.g., "AI"): Ask the LLM to identify 2-3 specific sub-narratives, pick the most actionable one
- Too narrow (e.g., "Company X's new product"): This is a single-stock thesis, suggest `/quick-check {ticker}` instead

---

## Timing Budget

| Phase | Target | Activity |
|-------|--------|----------|
| Phase 1 | ~3 min | LLM reasoning + 2-3 WebSearch |
| Phase 2 | ~5 min | 4-6 WebSearch + SEC search + market cap checks |
| Phase 3 | ~5 min | Parallel data fetch per candidate + scoring |
| Phase 4 | ~10-15 min | Sequential full evaluation (3-5 candidates × 3-4 min each) |
| **Total** | **~25-30 min** | |
