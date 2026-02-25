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

## Step 1: Environment & Capability Detection

Detect the runtime environment. Follow this sequence — stop at the first match:

### 1a. Check for Deep Research Tools

Look for `launch_extended_search_task`, `deep_research`, or any MCP tool with "research" in its name.

**If found → Branch B (Full Deep Research)**:
- Set `{research_mode}` = `"deep_research"`
- Proceed to Step 2

### 1b. Check for Code-Editing Tools

Look for: `Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `TodoWrite`, `Task`.

**If found → Branch A (Claude Code / Cowork)**:
- Set `{research_mode}` = `"websearch_fallback"`
- Proceed to Step 2

### 1c. Check for Claude.ai Signature Tools

Look for: `artifacts`, `analysis_tool`.

**If found → Branch C (Claude.ai)**:
- Offer Option A (Quick Research with WebSearch) or Option B (Enable Research mode)
- Wait for user choice, then proceed

### 1d. Fallback

- Set `{research_mode}` = `"websearch_fallback"`
- Proceed to Step 2

---

## Step 2: Stock Ticker Confirmation

Parse user input to identify the target stock:

**Single clear ticker** (e.g., "AAPL", "$TSLA", "苹果公司"):
- Use WebSearch to verify: `"{ticker} stock NYSE OR NASDAQ"`
- Confirm full company name, exchange, and ticker
- Set `{market}` = `US` (Phase 1 only supports US)
- Proceed to Step 3

**Multiple tickers**: List all detected, ask user to select ONE.

**Ambiguous input**: Ask user to specify a single company and ticker.

**Validation**: Confirm valid US-listed equity (NYSE/NASDAQ/AMEX). Reject OTC, foreign-only, or delisted tickers with explanation.

---

## Step 3: Language Detection & Parameter Setup

### 3a. Detect Language

- Chinese input → `{output_language}` = "中文"
- English input → `{output_language}` = "English"
- Other → match user's language

### 3b. Load Parameters

Read `references/thresholds.md` and `references/markets/us.md` to set:

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

## Step 4: Execute Research

### Phase 1 — Data Collection

Read and execute `skills/data-fetch/SKILL.md` with `{ticker}` and `{market}`.

This produces:
- Yahoo Finance structured data
- WebSearch source list (target 60+ unique)
- SEC EDGAR filings
- FRED macro data
- Coverage Log

### Phase 2 — Batch 1: Skeleton Sections

Read `references/investment_memo.md` with all parameters substituted.

Write the following critical sections first (300-600 words each):

1. **§1 Thesis Framework** — Investment thesis, pillars, variant view, "why now"
2. **§2 Market Structure & Size** — TAM/SAM, growth drivers, penetration
3. **§12 Financial Condition** — Revenue, margins, Rule of 40, FCF, leading indicators
4. **§13 Capital Structure** — Debt, leverage, WACC, liquidity
5. **§20 Valuation Framework** — Read and execute `skills/valuation/SKILL.md`
6. **§21 Scenarios & Catalysts** — Bear/base/bull scenarios, E[TR], catalysts, monitoring

Purpose: Establish thesis, financial foundation, and valuation anchors.

### Phase 3 — Batch 2: Remaining Sections

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

### Phase 5 — Output Validation

**Before saving the final memo**, read and execute `skills/output-validator/SKILL.md`.

The validator checks:
1. **Structural completeness** — All required components present
2. **Internal consistency** — Numbers match across sections (E[TR], fair value, rating logic)
3. **Writing standards** — Language, length, tagging, date formatting
4. **Coverage quality** — Source thresholds met or gaps acknowledged
5. **Risk & bias review** — Bull bias detection, disconfirming evidence check

**If validator returns FAIL**: Fix the flagged issues and re-run validator.
**If validator returns PASS or PASS WITH NOTES**: Proceed to output.

---

## Step 5: Output

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
├── references/thresholds.md        ← all threshold values
├── references/markets/{market}.md  ← market-specific config
├── references/investment_memo.md   ← section writing requirements only
├── skills/data-fetch/              ← data collection + coverage validation
├── skills/valuation/               ← DCF + comps + reverse DCF
├── skills/quality-scorecard/       ← 5-dimension quality scoring
├── skills/decision-rules/          ← 4-gate rating engine
└── skills/output-validator/        ← pre-output quality gate
```

Each skill is the **single source of truth** for its domain. No logic is duplicated across skills or in the memo template.
