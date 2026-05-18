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

## Step 3: Data Collection

Read and execute `skills/data-fetch/SKILL.md` with `{ticker}`, `{market}`, and `{mode}` = "full".

This produces:
- **Data Contract** — `Research/{ticker}/data_contract.md` (single source of truth for all quantitative data)
- Coverage Log (30+ unique sources)
- Coverage Validator (pass/fail for each criterion)
- Key qualitative findings organized by section relevance

**CRITICAL**: The Data Contract is the single source of truth for ALL quantitative data in the memo. All section-writers MUST reference `Research/{ticker}/data_contract.md` for financial numbers. No section may re-derive, estimate, or override Data Contract figures.

---

## Step 4: Financial Foundation (§2, §12, §13)

Read `references/investment_memo.md` (skill-local) with all parameters substituted.

**Before writing any section**, read `Research/{ticker}/data_contract.md` and use it as the authoritative source for all financial figures.

Write the following sections first (300-600 words each, except §12 which follows its expanded Key Assumptions Narrative requirements):

1. **§2 Market Structure & Size** — TAM/SAM, growth drivers, penetration
2. **§12 Financial Condition** — Revenue, margins, Rule of 40, FCF, leading indicators. Must include Key Assumptions Narrative per `investment_memo.md` requirements.
3. **§13 Capital Structure** — Debt, leverage, WACC, liquidity

Purpose: Establish financial foundation with quantitative data before any narrative.

---

## Step 5: Valuation (§20)

**CRITICAL — Valuation Independence Rule**: §20 must be written BEFORE §1 (Thesis) and §21 (Scenarios). This prevents narrative anchoring from biasing the valuation. The DCF and comps should produce a fair value range based purely on financial data and market structure — the thesis is then constructed around (and constrained by) the valuation output.

**Preliminary Peer Selection**: Before calling valuation, identify 5-8 comparable companies using Data Contract sector/industry fields + WebSearch. This peer list will be reused in §5 (Step 7) — do NOT rebuild from scratch. Pass it to the valuation skill.

4. **§20 Valuation Framework (800-1,200 words)** — Read and execute `skills/valuation/SKILL.md` with:
   - Financial data from `Research/{ticker}/data_contract.md`
   - Preliminary peer list (constructed above)
   - Market config from `references/markets/us.md`

**§20 must include all 5 sub-sections**: 20a (Comps with statistical summary rows), 20b (DCF with Sanity Check table), 20c (Reverse DCF), 20d (Fair Value Synthesis with Football Field + Scenario Valuation Table), 20e (Consensus Comparison). See `investment_memo.md` for detailed requirements.

---

## Step 6: Thesis & Scenarios (§1, §21)

Now write thesis and scenarios, constrained by the valuation output from Step 5:

5. **§1 Thesis Framework** — Investment thesis with structured pillar narratives (Market Opportunity / Capture Logic / Financial Impact / Falsification per pillar), variant view, "why now"
6. **§21 Scenarios & Catalysts (1,500-2,000 words)** — Must include all 4 sub-sections: 21a (Scenario Analysis with Key Assumptions tables), 21b (Scenario Comparison with narrative E[TR]), 21c (Growth Drivers), 21d (Catalysts & Monitoring). Bear case must comply with decision-rules Bear Case Construction Rules (minimum -20% return for beta ≥ 1.0 stocks).

**Cross-check**: If §1 thesis implies a fair value that diverges >20% from §20's DCF output, you MUST reconcile. Either adjust the thesis narrative or explain why the DCF is structurally conservative/aggressive.

Purpose: Ensure thesis is data-driven, not narrative-driven.

---

## Step 7: Remaining Sections (§3-§19)

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

---

## Step 8: Rating

1. **Quality Scorecard** — Read and execute `skills/quality-scorecard/SKILL.md` with:
   - Analysis content from all 21 sections (§1-§21)
   - Financial data from `Research/{ticker}/data_contract.md`

2. **Decision Rules** — Read and execute `skills/decision-rules/SKILL.md` with:
   - Valuation outputs from §20 (Fair Value Range, Buy/Trim Zones)
   - Scenario parameters from §21 (Bear/Base/Bull per-scenario returns, probabilities, E[TR], catalysts)
   - Quality Score from quality-scorecard
   - Thresholds from `references/markets/us.md`
   Output feeds into Executive Summary Gate table, NOT a standalone section.

---

## Step 9: Report Assembly & Validation

**This step is MANDATORY — do NOT skip it regardless of context window constraints.**

### Phase A — Assembly

1. Assemble the report in this order:
   - Executive Summary (write LAST, based on all prior analysis — the ONLY place for rating, gate decisions, and entry zones)
   - Quality Scorecard
   - §1-§21
   - Coverage Log + Coverage Validator
   - Appendix (must include Projected Financial Model table consistent with §20 DCF)
2. Write Executive Summary last, after all other content is finalized

### Phase B — Data Reconciliation

Cross-check key numbers across sections. **All items must pass**:

- E[TR]: §21 = Executive Summary = Decision Rules (single value, no rounding differences)
- Fair Value Range / Buy Trim Zones: §20 = Executive Summary = Decision Rules
- Quality Score: Scorecard total = Executive Summary
- Revenue figures: §12 = §9 decomposition total
- Current Price: Same across all sections
- Scenario probabilities: Bull + Base + Bear = 100%
- §21 bear case total return ≥ -20% (when beta ≥ 1.0)
- §20 comps statistical summary (Max/75th/Median/25th/Min) correctly computed
- **Data Provenance Audit**: 报告中所有量化字段（目标股财务、peer 倍数、宏观参数、合同金额、客户份额、运营指标等）必须能追溯到 `Research/{ticker}/data_contract.md` 中带时间戳的具体抓取记录。任何字段以 "~"、"约"、"approximately"、"市场近似值" 等措辞出现于数值位置 = FAIL，必须用 MCP / 脚本 / 公开披露文件重新抓取并标注。**Peer 数据 Pull Date 必须 = 研究当天**——每次研究重新抓取最新数据，不复用任何历史快照。规则行业中立——任何 ticker 任何行业一视同仁。详见 `tasks/lessons.md` 2026-05-19 条目。
- Rating vs. Gates: Rating = Buy only if all 4 gates pass + Quality ≥ 70
- Appendix Projected Financial Model reconciles with §20 DCF projections

**If any mismatch**: Resolve by recalculating from the source skill's output, not by averaging.

### Phase C — Writing Quality Polish

Scan the entire assembled report and apply the following transformations:

1. **Remove all internal tags**: Delete every instance of `(Fact)` / `(Analysis)` / `(Inference)` / `Cross-reference §XX` / `Purpose —`
2. **Symbol cleanup**: Replace any remaining `■` with bold-topic paragraph format; replace `→` used as causal/trend indicator with complete sentences
3. **Naked table remediation**: Every table must have 1-2 sentences before and after it explaining context and implications
4. **Approximate value sourcing**: Replace `~60%` with sourced form, e.g., "约 60%（管理层 Q2 指引）"
5. **Calculation narrative embedding**: Convert raw formulas (e.g., `E[TR] = 25% × 77.8% + ...`) into narrative descriptions
6. **Placeholder removal**: Delete any `[TODO]`, `[TBD]`, `{variable}` placeholders
7. **Verify bold-topic format**: Each section's core analysis uses `**Bold header.** Detail sentences.` format (not ■ bullets)

### Phase D — Validation Checks

Run all 5 checks below before saving:

#### Check 1: Structural Completeness

Verify all required components exist: Executive Summary (Rating Box with Gate table, Entry Zones, Thesis, Risks, Catalysts, Change Triggers), Quality Scorecard (5 dimensions + total), Sections 1-21 (§17 may be N/A if no hardware), Coverage Log, Coverage Validator, Appendix (DCF model + sensitivity table + Projected Financial Model).

- §20 contains sub-sections 20a through 20e (Comps with stats, DCF with sanity check, Reverse DCF, Fair Value with Football Field, Consensus Comparison)
- §21 contains sub-sections 21a through 21d (Scenario Analysis with assumptions tables, Scenario Comparison, Growth Drivers, Catalysts & Monitoring)
- **Minimum table count**: ≥ 12 tables (Financial Summary, Peer Comparison, DCF Sensitivity, DCF Sanity Check, Scenario Assumptions, Scenario Comparison are mandatory)
- **Assumption documentation**: Appendix key assumptions narrative ≥ 1,000 words

**If any component is missing**: Draft it before proceeding.

#### Check 2: Writing Standards

- Language: Entire memo in `{output_language}`
- Section length: §1-§19 each 300-600 words; §20 800-1,200 words; §21 1,500-2,000 words
- Total length: 10,000-12,000 words
- Language consistency: No unintended language mixing within paragraphs
- No placeholders: Zero instances of `[TODO]`, `[TBD]`, `{variable}`
- No internal tags: Zero instances of `(Fact)`, `(Analysis)`, `(Inference)`, `Cross-reference §`, `Purpose —`
- Dates: No "recently" or "last quarter" — exact dates only
- Calculations: Embedded in narrative, not as raw formulas
- Acronyms: Expanded on first use
- **Source attribution**: Every table has a `Source:` line
- **A/E notation**: All year data uses FYxxxxA / FYxxxxE format
- **Paragraph format**: Bold-topic paragraphs (not ■ bullets)
- **Notation consistency**: Multiples use Xx format, currency uses $XXB/$XXM format

#### Check 3: Coverage Quality

Review the Coverage Log and Validator from data-fetch:
- Total unique sources ≥ 30
- Source types covered ≥ 4 of 6 (SEC Filings / Earnings-IR / Industry Report / Quality Media / Competitor Primary / Academic-Expert)
- MCP data populated ≥ 80% of Data Contract fields
- Sources within 12 months ≥ 50%

**If any criterion fails**: Do NOT block output. Append a Research Methodology Note stating which criteria fell short.

#### Check 4: Risk & Bias Review

- Bull bias: Is the rating justified by evidence, or overly optimistic?
- Bear acknowledgment: Are bear-case risks clearly stated with quantified impact?
- Disconfirming evidence: At least one disconfirming source cited?
- Assumption transparency: Key assumptions (growth rate, margin, discount rate) explicitly stated?
- Conflict check: Do thesis pillars and risk factors logically coexist?

**If bull bias detected**: Add a "Devil's Advocate" paragraph in the Executive Summary.

#### Check 5: Cross-Report Consistency (if applicable)

Search `Research/{ticker}/` for any prior memos or quick-checks within the last 30 days.

If found:
- Compare fair value mid: if delta > 20%, MUST add a "Valuation Delta" callout in the Executive Summary explaining what changed
- Compare WACC, beta, terminal growth assumptions: any change must have an explicit justification tied to new data (not just "different methodology")
- Compare rating: if rating changed (e.g., Hold → Buy), state the specific new evidence that triggered the change
- If no fundamental change occurred (no new earnings, no guidance update, no macro shift), flag that the valuation delta may reflect modeling assumption drift rather than genuine re-rating

**If delta > 20% with no new data**: This is a FAIL. Reconcile the assumptions before finalizing.

#### Result Handling

- **PASS** → Proceed to Step 10
- **PASS WITH NOTES** → Append notes, proceed to Step 10
- **FAIL** → Fix flagged issues and re-run all 5 checks
- **Context window low** → Run Check 1 (structural) + Phase B (data reconciliation) + Check 5 (cross-report) only, append note that full validation was not completed

---

## Step 10: Output

### Output Sequence

```
1. Executive Summary (includes Rating Box, Gate table, Entry Zones — all in one place)
2. Quality Scorecard (standalone — substantive scoring breakdown)
3. Sections 1-21
4. Coverage Log + Coverage Validator
5. Appendix (includes Projected Financial Model)
```

**No standalone sections for**: Rating & Target Price, Investment Thesis & Variant View, Decision Rules, Entry Readiness Assessment. These are either in Executive Summary or in their respective §sections.

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
3. **Report Assembly & Validation** (Step 9) is mandatory — the memo cannot be saved without passing all checks and writing quality polish.
