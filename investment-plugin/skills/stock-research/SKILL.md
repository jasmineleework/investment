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

## Step 3: Data Collection — Target

Read and execute `skills/data-fetch/SKILL.md` with `{ticker}`, `{peer_set}` = `[]`, `{market}`, and `{mode}` = "full".

This produces the **Data Contract v1** at `Research/{ticker}/data_contract.md` covering the target only. The `## Peer Data` section is rendered empty at this stage; it will be filled by a `supplement` call from Step 4.5 below.

Also produced:
- Coverage Log (30+ unique sources)
- Coverage Validator (pass/fail for each criterion)
- Key qualitative findings organized by section relevance

**CRITICAL**: The Data Contract is the single source of truth for ALL quantitative data in the memo. All section-writers MUST reference `Research/{ticker}/data_contract.md` for financial numbers. No section may re-derive, estimate, or override Data Contract figures.

The Data Contract is **append-only** within a research run: supplement calls may add `## Peer Data` rows, but no section ever mutates or deletes existing rows. The report (memo) is a filtered view of the Contract — it may exclude individual peer rows via "Outlier Exclusions" subsections, but the Contract retains everything fetched.

---

## Step 4: All Analytical Sections (§2–§19)

Write the analytical sections in numerical order. The Data Contract is the source of truth for quantitative data; the Coverage Log + qualitative research from data-fetch is the basis for qualitative analysis.

**Section ordering rationale**: All 18 analytical sections come BEFORE §20 Valuation so that valuation rests on full business understanding (competitive position, monetization quality, unit economics, etc.) rather than financial snapshots alone. §1 Thesis and §21 Scenarios come AFTER §20 — they synthesize analysis + valuation, preserving the Valuation Independence Rule (no narrative anchoring of §20).

Write each section 300–600 words (except §12 which follows its expanded Key Assumptions Narrative requirements per `investment_memo.md`).

### Step 4.1: §2 Market Structure & Size

TAM/SAM, growth drivers, penetration. Quantitative data from Data Contract.

### Step 4.2: §3 Customer Segmentation & Demand

### Step 4.3: §4 Product & Roadmap

### Step 4.4: §5a Competitive Landscape — Identification only

Identify 5–8 direct competitors based on §3 (customer overlap) and §4 (product overlap) plus WebSearch. For each peer, record a 1-line rationale (business model similarity, scale, geography, customer overlap).

| Peer Ticker | Reason for inclusion (1 line) |
|-------------|--------------------------------|
| PEER_1      | ...                            |
| ...         | ...                            |

Output: `{peer_set}` = list of 5–8 ticker symbols.

**Do NOT fill Template B Peer Comparison yet** — peer financials have not been fetched. Template B is completed in §5b after Step 4.5.

### Step 4.5: Peer Data Supplement Fetch

Read and execute `skills/data-fetch/SKILL.md` with:
- `{ticker}` (target, unchanged)
- `{peer_set}` from Step 4.4
- `{market}` (unchanged)
- `{mode}` = `"supplement"`

This appends the `## Peer Data` section to the existing Data Contract. Every row's `Pull Date` must equal the research day (today).

### Step 4.6: §5b Competitive Dynamics + Template B

Fill Template B Peer Comparison from the Data Contract's `## Peer Data` section. Write §5b prose covering competitive position, market share dynamics, moat differentiation.

If at this stage you judge a fetched peer is structurally non-comparable, document the exclusion in a §5b "Outlier Exclusions" subsection with reason. **Do NOT remove the row from the Data Contract** — it stays as audit record. Template B includes only the peers you actually use; the Data Contract may contain more rows.

### Step 4.7–4.20: §6 through §19

Write the remaining analytical sections in numerical order.

**On-demand supplement is available at any analytical step.** Two trigger types:

- **Peer supplement** — if a section surfaces additional peer candidates whose data would meaningfully shift the analysis (e.g., §10 Pricing Power benchmark requires an unconsidered peer), invoke `data-fetch(mode=supplement, peer_set=[NEW_TICKER])`. New rows append to `## Peer Data`. Document the addition in §5b or wherever the peer is invoked.
- **Research supplement** — if a section needs additional qualitative material beyond the initial Coverage Log (e.g., §15 Data & AI Economics needs specifics on a recent chip launch; §17 Supply Chain needs supplier disclosure; §18 Risk Inventory needs litigation timeline), invoke `data-fetch(mode=supplement, topics=["{focused query}"])`. WebSearch findings append to `## Research Supplement` with full source citations and timestamps. Cite the block reference (e.g., "see Research Supplement 2026-05-19 #2") in the section's prose.

Both supplement types may be combined in one call when a section needs both kinds of material. The Data Contract retains every supplement entry as an append-only audit record. Trigger supplements whenever the analysis genuinely benefits — do NOT pad with low-value queries; each call should have a stated reason in the triggering section's text.

Sections to write (in order):

- §6 Ecosystem & Platform Health
- §7 Go-to-Market & Distribution
- §8 Retention & Expansion
- §9 Monetization Model & Revenue Quality
- §10 Pricing Power & Elasticity
- §11 Unit Economics & Efficiency
- §12 Financial Condition — Revenue, margins, Rule of 40, FCF, leading indicators. Must include Key Assumptions Narrative per `investment_memo.md`.
- §13 Capital Structure — Debt, leverage, WACC, liquidity. WACC inputs feed §20 DCF.
- §14 Moat & Data Advantage
- §15 Data & AI Economics
- §16 Execution Quality & Organization
- §17 Supply Chain & Operations
- §18 Risk Inventory & Mitigations
- §19 M&A Strategy & Optionality

Purpose: Complete company-level deep analysis before valuation, so §20's DCF/Comps assumptions are grounded in full business understanding rather than financial snapshots alone.

---

## Step 5: §20 Valuation

**Valuation comes AFTER all 18 analytical sections (§2–§19) are complete.** This ordering ensures the DCF growth/margin/capex assumptions, the comps premium/discount judgment, and the Reverse DCF reasonableness check all rest on the analytical work just completed.

**CRITICAL — Valuation Independence Rule**: §20 must be written BEFORE §1 (Thesis) and §21 (Scenarios). This prevents narrative anchoring from biasing the valuation. The DCF and comps should produce a fair value range based on financial data and competitive analysis — the thesis is then constructed around (and constrained by) the valuation output.

Read and execute `skills/valuation/SKILL.md` with:
- Data Contract path: `Research/{ticker}/data_contract.md` (contains target rows + `## Peer Data` populated in Step 4.5)
- Market config from `references/markets/us.md`

**§20 must include all 5 sub-sections**: 20a (Comps with statistical summary rows), 20b (DCF with Sanity Check table), 20c (Reverse DCF), 20d (Fair Value Synthesis with Football Field + Scenario Valuation Table), 20e (Consensus Comparison). See `investment_memo.md` for detailed requirements.

If §20a Comps surfaces a need for additional peer benchmarks not in the current Peer Data section, you may invoke another `data-fetch(mode=supplement)` here as a last opportunity to extend the peer set. Document the rationale in §20a.

---

## Step 6: Thesis & Scenarios (§1, §21)

§1 Thesis and §21 Scenarios come LAST — they synthesize the entire memo including the §20 valuation result.

1. **§1 Thesis Framework** — Investment thesis with structured pillar narratives (Market Opportunity / Capture Logic / Financial Impact / Falsification per pillar), variant view, "why now"
2. **§21 Scenarios & Catalysts (1,500–2,000 words)** — Must include all 4 sub-sections: 21a (Scenario Analysis with Key Assumptions tables), 21b (Scenario Comparison with narrative E[TR]), 21c (Growth Drivers), 21d (Catalysts & Monitoring). Bear case must comply with decision-rules Bear Case Construction Rules (minimum -20% return for beta ≥ 1.0 stocks).

**Cross-check**: If §1 thesis implies a fair value that diverges >20% from §20's DCF output, you MUST reconcile. Either adjust the thesis narrative or explain why the DCF is structurally conservative/aggressive — do NOT silently retune §20.

Purpose: Ensure thesis is data-driven and valuation-anchored, not narrative-driven.

---

## Step 7: Rating

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
- **Data Provenance Audit**: 报告中所有量化字段（目标股财务、peer 倍数、宏观参数、合同金额、客户份额、运营指标等）必须能追溯到 `Research/{ticker}/data_contract.md` 中带时间戳的具体抓取记录。任何字段以 "~"、"约"、"approximately"、"市场近似值" 等措辞出现于数值位置 = FAIL，必须用 MCP / 脚本 / 公开披露文件重新抓取并标注。**Peer 数据 Pull Date 必须 = 研究当天**——每次研究重新抓取最新数据，不复用任何历史快照。规则行业中立——任何 ticker 任何行业一视同仁。运行 `python3 investment-plugin/skills/data-fetch/scripts/validate_data_contract.py Research/{ticker}/data_contract.md` 自动检查；非零退出码 = FAIL。详见 `tasks/lessons.md` 2026-05-19 条目。
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

Run all 6 checks below before saving. **Check 0 is machine-enforced** (hard fail on non-zero exit); Checks 1-5 are LLM judgment.

#### Check 0: Format Lint (machine-enforced — RUN FIRST)

Run the validator on the assembled memo:

```bash
python3 investment-plugin/skills/stock-research/scripts/validate_memo_format.py Research/{ticker}/{date}_memo.md
```

Non-zero exit code = **FAIL**. This is a hard gate — fix every violation and re-run before proceeding to Checks 1-5. Three hard constraints checked:

- **C1 Buy/Trim Zone**: Executive Summary MUST contain both a `| Buy Zone | $X – $Y | Initiate position |` row and a `| Trim Zone | ... |` row (per `references/investment_memo.md` L165-167). Free-text descriptions like "Buy Zone Low = $174" do NOT count — `morning-update` skill's `memo_loader.py` requires the table-row format.
- **C2 Pillar titles**: §1 MUST contain ≥3 pillar titles in `**Thesis Pillar N: <title>**` or `**Pillar N: <title>**` form. **N must be an Arabic digit** (1, 2, 3, …). Chinese ordinals like `**支柱一：...**` are forbidden — they break the downstream parser. (Source: template L294.)
- **C3 Catalyst dates**: §21d catalyst table MUST contain ≥1 row whose first cell is a strict `YYYY-MM-DD` date (annotations like `(est.)` are fine). Quarter labels (`2026Q2`, `2026 H1`, `持续`, `2027 上半年`) alone do NOT satisfy — `morning-update` parses these as misses. Mixing some YYYY-MM-DD rows with some quarter rows is a WARN (not FAIL).

**Why this matters**: `Research/CRWV/2026-05-19_memo.md` shipped without these constraints and broke `morning-update` Part 3 entirely (0 zone signals, 0 catalysts detected). The validator catches all three classes of CRWV's failures.

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
- **FAIL** → Fix flagged issues and re-run **Check 0 first** (machine), then Checks 1-5
- **Context window low** → Check 0 + Check 1 (structural) + Phase B (data reconciliation) + Check 5 (cross-report); skip Checks 2-4 and append a note. **Check 0 is non-negotiable** — sub-second script call, no excuse to skip.

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
