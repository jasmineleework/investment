---
name: stock-research
description: >
  US stock deep research and investment memo generation.
  Triggers when the user asks to analyze, research, or evaluate
  a US stock (e.g., "analyze AAPL", "research Tesla",
  "帮我分析英伟达", "NVDA deep dive", "美股研报").
  Produces a comprehensive investment memorandum with
  Buy/Hold/Sell rating following institutional standards.
---

# Stock Research — Main Orchestrator

Generate institutional-grade investment memos for US-listed stocks. This skill orchestrates data-fetch, quality-scorecard, valuation, and decision-rules skills to produce a complete, decision-ready research memorandum.

---

## Step 1: Stock Ticker Confirmation

Parse user input to identify the target stock:

**Single clear ticker** (e.g., "AAPL", "$TSLA", "苹果公司"):
- Use WebSearch to verify: `"{ticker} stock NYSE OR NASDAQ"`
- Confirm full company name, exchange, and ticker
- Set `{market}` = `US` (Phase 1 only supports US)
- Proceed to Step 2

**Multiple tickers**: List all detected, ask user to select ONE.

**Ambiguous input**: Ask user to specify a single company and ticker.

**Validation**: Confirm valid US-listed equity (NYSE/NASDAQ/AMEX). Reject OTC, foreign-only, or delisted tickers with explanation.

---

## Step 2: Language Detection & Parameter Setup

### 2a. Detect Language

- Chinese input → `{output_language}` = "中文"
- English input → `{output_language}` = "English"
- Other → match user's language

### 2b. Load Parameters

Read `references/markets/us.md` (contains both market config and decision thresholds) to set:

| Variable | Value |
|----------|-------|
| {stock_name} | Confirmed company name |
| {stock_ticker} | Confirmed ticker |
| {output_language} | Detected language |
| {market} | US |
| {benchmark} | S&P 500 |
| {currency} | USD |
| {MOS_%} | 25% |
| {SKEW_X} | 1.7× |
| {QUALITY_PASS} | 70 |
| {QUALITY_SELL} | 60 |
| {HURDLE_TR_%} | 30% |
| {HORIZON} | 24 months |

---

## Step 3: Execute Research

### Phase 1 — Data Collection & Data Contract

Read and execute `skills/data-fetch/SKILL.md` with `{ticker}`, `{market}`, and `{mode}` = "full".

This produces:
- **Data Contract** — `Research/{ticker}/data_contract.md` (single source of truth for all quantitative data)
- Coverage Log (30+ unique sources)
- Coverage Validator (pass/fail for each criterion)
- Key qualitative findings organized by section relevance

**CRITICAL**: The Data Contract is the single source of truth for ALL quantitative data in the memo. All section-writers MUST reference `Research/{ticker}/data_contract.md` for financial numbers. No section may re-derive, estimate, or override Data Contract figures.

### Phase 2 — Batch 1: Skeleton Sections

Read `references/investment_memo.md` (skill-local) with all parameters substituted.

**Before writing any section**, read `Research/{ticker}/data_contract.md` and use it as the authoritative source for all financial figures.

Write the following critical sections first (300-600 words each):

1. **§1 Thesis Framework** — Investment thesis, pillars, variant view, "why now"
2. **§2 Market Structure & Size** — TAM/SAM, growth drivers, penetration
3. **§12 Financial Condition** — Revenue, margins, Rule of 40, FCF, leading indicators
4. **§13 Capital Structure** — Debt, leverage, WACC, liquidity
5. **§20 Valuation Framework** — Read and execute `skills/valuation/SKILL.md`
6. **§21 Scenarios & Catalysts** — Bear/base/bull scenarios, E[TR], catalysts, monitoring

Purpose: Establish thesis, financial foundation, and valuation anchors.

### Phase 3 — Batch 2: Remaining Sections

**Reminder**: All financial data must come from `Research/{ticker}/data_contract.md`.

Write remaining sections (300-600 words each):

- §3 Customer Segmentation & Demand
- §4 Product & Roadmap
- §5 Competitive Landscape
- §6 Ecosystem & Platform Health
- §7 Go-to-Market & Distribution
- §8 Retention & Expansion
- §9 Monetization Model & Revenue Quality
- §10 Pricing Power & Elasticity
- §11 Unit Economics & Efficiency
- §14 Moat & Data Advantage
- §15 Data & AI Economics
- §16 Execution Quality & Organization
- §17 Supply Chain & Operations
- §18 Risk Inventory & Mitigations
- §19 M&A Strategy & Optionality

Purpose: Complete company-level deep analysis.

### Phase 4 — Batch 3: Rating & Assembly

1. **Quality Scorecard** — Read and execute `skills/quality-scorecard/SKILL.md`
2. **Decision Rules** — Read and execute `skills/decision-rules/SKILL.md`
3. **Entry Readiness Assessment** — Based on decision-rules output
4. **Executive Summary** — Write LAST, based on all prior analysis:
   - Rating, Fair Value Range, Expected Total Return
   - Buy/Trim Zones, Dated Catalysts
   - What Would Change This Rating
5. **Coverage Log + Coverage Validator** — From data-fetch output
6. **Appendix** — Models, data tables, key assumptions

### Phase 5 — Output Validation (MANDATORY)

**This phase is MANDATORY — do NOT skip it regardless of context window constraints.**

Before saving the final memo, run all 5 checks below:

#### Check 1: Structural Completeness

Verify all required components exist: Executive Summary (Rating, Fair Value Range, E[TR], Buy/Trim Zones, Catalysts, Change Triggers), Rating & Target Price, Investment Thesis & Variant View, Quality Scorecard (5 dimensions + total), Decision Rules (4 gates), Entry Readiness Assessment, Sections 1-21 (§17 may be N/A if no hardware), Coverage Log, Coverage Validator, Appendix (DCF model + sensitivity table minimum).

**If any component is missing**: Draft it before proceeding.

#### Check 2: Internal Consistency

Cross-check key numbers across sections:
- Rating vs. Gates: Rating = Buy only if all 4 gates pass + Quality ≥ 70
- E[TR]: §21 = Executive Summary = Decision Rules
- Fair Value Range: §20 = Executive Summary = Decision Rules
- Quality Score: Scorecard total = 5-dimension weighted sum × 20
- Scenario probabilities: Bull + Base + Bear = 100%
- Buy/Trim Zones: Derived from Fair Value per valuation skill formula
- Revenue figures: §12 = §9 decomposition total
- Current price: Same across all sections

**If any mismatch**: Resolve by recalculating from the source skill's output, not by averaging.

#### Check 3: Writing Standards

- Language: Entire memo in `{output_language}`
- Section length: Each section 300-600 words
- Total length: 8,000-10,000 words
- Tagging: Every paragraph tagged (Fact)/(Analysis)/(Inference)
- Dates: No "recently" or "last quarter" — exact dates only
- Calculations shown: Key estimates have visible math
- Acronyms: Expanded on first use

#### Check 4: Coverage Quality

Review the Coverage Log and Validator from data-fetch:
- Total unique sources ≥ 30
- Source types covered ≥ 4 of 6 (SEC Filings / Earnings-IR / Industry Report / Quality Media / Competitor Primary / Academic-Expert)
- MCP data populated ≥ 80% of Data Contract fields
- Sources within 12 months ≥ 50%

**If any criterion fails**: Do NOT block output. Append a Research Methodology Note stating which criteria fell short.

#### Check 5: Risk & Bias Review

- Bull bias: Is the rating justified by evidence, or overly optimistic?
- Bear acknowledgment: Are bear-case risks clearly stated with quantified impact?
- Disconfirming evidence: At least one disconfirming source cited?
- Assumption transparency: Key assumptions (growth rate, margin, discount rate) explicitly stated?
- Conflict check: Do thesis pillars and risk factors logically coexist?

**If bull bias detected**: Add a "Devil's Advocate" paragraph in the Executive Summary.

#### Result Handling

- **PASS** → Proceed to output
- **PASS WITH NOTES** → Append notes, proceed to output
- **FAIL** → Fix flagged issues and re-run all 5 checks
- **Context window low** → Run Check 1 + Check 2 only, append note that full validation was not completed

---

## Step 4: Output

### Output Sequence

```
1. Executive Summary
2. Rating & Target Price
3. Investment Thesis & Variant View
4. Decision Rules / Quality Scorecard / Entry Assessment
5. Sections 1-21
6. Coverage Log + Coverage Validator
7. Appendix
```

### File Output

Save to: `{workspace}/Research/{stock_ticker}/{date}_memo.md`

Where:
- `{workspace}` = current working directory or Cowork workspace folder
- `{date}` = today's date in YYYY-MM-DD format

---

## Skill Dependency Map

```
stock-research (this skill)
├── references/investment_memo.md       ← section writing requirements (skill-local)
├── references/markets/{market}.md      ← market config + decision thresholds (plugin-level, shared)
├── skills/data-fetch/                  ← data collection + Data Contract + coverage validation
│   └── Research/{ticker}/data_contract.md  ← SINGLE SOURCE OF TRUTH for all quantitative data
├── skills/valuation/                   ← DCF + comps + reverse DCF
├── skills/quality-scorecard/           ← 5-dimension quality scoring (industry-adaptive)
└── skills/decision-rules/              ← 4-gate rating engine
```

**Key Principles**:
1. Each skill is the **single source of truth** for its domain. No logic is duplicated.
2. The **Data Contract** (`data_contract.md`) is the single source of truth for quantitative data — all sections must reference it.
3. **Output Validation** (Phase 5) is mandatory and inline — the memo cannot be saved without passing all 5 checks.
