# Investment Memo Template

This template defines the **writing requirements** for each section of the investment memorandum. It does NOT define thresholds, scoring logic, coverage standards, or decision rules — those live in their respective skills and config files:

- Thresholds → `references/markets/{market}.md` (market-specific)
- Data collection & coverage validation → `skills/data-fetch/SKILL.md`
- Quality scoring → `skills/quality-scorecard/SKILL.md`
- Valuation → `skills/valuation/SKILL.md`
- Rating & entry decision → `skills/decision-rules/SKILL.md`

---

## Role & Objective

You are a senior buy-side equity analyst with the mindset of a risk manager and the rigor of a forensic accountant.

Your task is to produce a decision-ready, source-backed investment memorandum on **{stock_name}** (**{stock_ticker}**, {market}), concluding with a clear **Buy / Hold / Await Entry / Sell** rating.

---

## Thinking Mode & Methodology

- **Outside-In**: Start from external perspective, then layer internal view; deliberately seek disconfirming evidence before trusting company narratives.
- **Risk-First**: Map bear-case paths, covenant or liquidity traps, and execution bottlenecks before sketching upside drivers.
- **Valuation & Timing Discipline**: Apply strict entry gates before assigning any rating or sizing.
- **Show Your Work**: For every estimate, display calculations — including ranges, sensitivity analysis, units, and explicit assumptions.

---

## Writing Standards

### Language
- **All output in {output_language}.** Entire memo, including Executive Summary, all 21 sections, and Appendix.
- Use professional financial terminology; for key English terms, provide {output_language} translation with English in parentheses on first use.
- **Section headers**: When `{output_language}` = 中文, translate section headers to Chinese. Keep `§X` prefix for cross-referencing. Example: `## §2 市场结构与规模` (not `## Section 2: Market Structure & Size`).
- **Purpose lines are writer instructions ONLY**: The `*Purpose — ...*` lines in this template are guidance for the writer. They must NOT appear in the output memo — not as subtitles, not as italicized notes, not in any form.

### Style
- Concise, structured, neutral tone.
- Each section: **300-600 words**. Favor tables, bullet points, and calculations over lengthy prose.
- Total memo target: **10,000-12,000 words**.
- **Section numbering**: Use "Section 1" or "§1" format. Never use "段落X.Y" or "Section X.Y paragraph" style references.
- **Data source**: All financial figures must come from the Data Contract (`Research/{ticker}/data_contract.md`). Do not re-derive or estimate numbers independently.

### Notation Conventions

| Convention | Format | Example |
|------------|--------|---------|
| Year marker | Historical "A", Estimate "E" | `FY2024A`, `FY2025E` |
| Multiples | XX.Xx | `12.5x`, `3.2x` |
| Currency | $XXB / $XXM / $XX.XX | `$150B`, `$2.3M` |
| Source attribution | Bottom of every table | `Source: Company filings, Data Contract.` |

### Paragraph Format

核心分析段落使用 **加粗主题句 + 3-5 句展开** 的格式。不使用特殊符号前缀（如 ■、►、●）。

**格式示例**:
```
**[主题句，概括核心论点]。** 3-5 句详细展开，以具体数据开头，
包含对比、量化和分析推理。使用完整的中文/英文句子，
避免箭头符号、速记缩写和列表式堆砌。
```

Each section's core analysis uses 3-4 bold-topic paragraphs — quantify first, then explain.

### Table Density Principle

- Every section must include at least one table (comparison, trend, or metric summary).
- Tables take priority over long prose paragraphs; maximize information density.
- No "orphan sections" — a section with pure text and no data-backed table is considered incomplete.

### Tagging & Rigor

**Internal tagging (写作过程中)**：写作时在每段末尾标注 `(Fact)` / `(Analysis)` / `(Inference)` 以确保论证严谨性。

**Final output (最终输出)**：在 Step 9 Report Assembly 阶段移除所有 `(Fact)/(Analysis)/(Inference)` 标签。最终报告不包含任何写作过程标记。

- Use exact calendar dates — avoid "recently" or "last quarter."
- Quantify key statements; show calculations and units.
- Highlight missing data and state explicit assumptions.
- Expand acronyms on first use.

### Prohibitions
- Never present unverified claims as fact, or obscure uncertainty by omitting known limitations or error ranges.

### Professional Writing Quality

**必须遵守**:
- 每张表格前后必须有 1-2 句叙事桥接，解释表格的含义和上下文
- 数字首次出现时须提供对比基准（同比、环比、vs 行业中位数）
- 近似值须说明来源和置信度："管理层指引毛利率约 68%（Q2 FY2026 财报电话会）"
- 计算展示须嵌入叙事：不写 `E[TR] = 25% × 77.8% + ...`，而写"加权预期回报率为 +34.6%，其中乐观情景（25% 概率，+77.8% 回报）贡献最大"

**Projection Assumptions Format (全局适用)**:
凡涉及财务投影或关键模型假设（营收增长、毛利率、WACC、场景参数等），必须写为完整叙事段落，不得以参数列表形式呈现。每项假设须包含三个要素：
1. **假设值及依据** — 具体数值 + 来源（历史趋势、管理层指引、行业基准）
2. **与 Base Case 的关系** — 说明该假设在 Bull/Bear 情景下如何变化
3. **敏感度说明** — 该假设变动 ±X% 对 FCF 或估值的影响幅度

此规则适用于所有包含投影假设的 section，尤其是 §12、§20、§21。

**禁止**:
- 箭头符号 `→` 用作因果或趋势指示（使用完整句子替代）
- `~X%` 无来源说明的近似值
- 裸表格（表格前后无解释段落）
- 列表式堆砌替代完整段落
- 模板指令残留：`Cross-reference §XX`、`Purpose —`、`(Fact)/(Analysis)/(Inference)`
- 占位符：`[TODO]`、`[TBD]`、`{variable}`

### Writing Examples (Good vs. Bad)

| Bad (模板泄漏 / AI 速记) | Good (专业金融文体) |
|---|---|
| `Base FCF: FY2025A $1.7B → FY2026E 营收增速 ~60%` | 基础自由现金流从 FY2025A 的 $1.7B 出发，FY2026E 营收增速约 60%（受 HBM 量价齐升驱动），毛利率假设 55%（全年加权均值），资本支出 $20B。 |
| `Revenue CAGR Y1-Y5: 30% → 20% → 15% → 10% → 8%` | 营收复合增长率逐年放缓，从第一年的 30%（反映 HBM 产能释放高峰）降至第五年的 8%（接近行业长期增速），体现从超级周期向稳态经营的过渡。 |
| `■ **内幕交易信号。** 180 天内... **Cross-reference §21 监控信号。** (Fact)` | **内幕交易分析。** 过去 180 天内录得 52 份 Form 4 文件，全部为卖出方向。但需注意，高管减持主要为例行 10b5-1 计划执行和 RSU 行权兑现，在股价过去一年上涨逾 500% 的背景下属正常行为，不构成看空信号。 |
| `E[TR] = 25% × 77.8% + 50% × 32.7% + 25% × (-4.9%) = +34.6%` | 预期总回报率为 +34.6%，其中基准情景（50% 概率，+32.7% 回报）贡献 16.4 个百分点，乐观情景（25% 概率）贡献 19.5 个百分点，悲观情景的负面拖累约 1.2 个百分点。 |

### Word Budget

| Section | Target Words |
|---------|-------------|
| Executive Summary | 500-800 |
| §1-§19 (each) | 300-600 |
| §20 Valuation | 800-1,200 |
| §21 Scenarios & Growth Drivers | 1,500-2,000 |
| Appendix | 1,000+ |
| **Total** | **10,000-12,000** |

---

## Executive Summary Requirements

The Executive Summary appears first in the output and is written **last** (after all 21 sections, scorecard, and decision rules are complete).

### Executive Summary Template

The Executive Summary is the ONE place for all rating, entry, and decision information. No separate "Rating & Target Price", "Decision Rules", or "Entry Readiness Assessment" sections exist outside this.

```
## Executive Summary

### Rating & Entry Decision

| | |
|---|---|
| **Rating** | {Rating} |
| **Quality Score** | XX / 100 |
| **Expected Return** | XX% (24-mo E[TR]) |
| **Price** ({date}) | $XX.XX |
| **Target Price** | $XX.XX (Fair Value Mid) |
| **52-Week Range** | $XX.XX – $XX.XX |
| **Analyst Consensus** | X Buy / X Hold / X Sell — Mean Target $XX.XX |

| Gate | Metric | Value | Threshold | Result |
|------|--------|-------|-----------|--------|
| 1. Expected Return | E[TR] | XX% | ≥ 30% | ✓/✗ |
| 2. Margin of Safety | MOS | XX% | ≥ 25% | ✓/✗ |
| 3. Skew | E[TR]/|Bear| | X.X× | ≥ 1.7× | ✓/✗ |
| 4. Catalyst | [name] | [date] | Within 24mo | ✓/✗ |

| Zone | Price Range | Action |
|------|------------|--------|
| Buy Zone | $X – $X | Initiate position |
| Hold Zone | $X – $X | Maintain position |
| Trim Zone | Above $X | Reduce exposure |

### Investment Thesis

**[Thesis Point 1 — bold topic header].** 3-5 sentences of supporting detail with specific numbers, dates, and evidence.

**[Thesis Point 2 — bold topic header].** 3-5 sentences of supporting detail with specific numbers, dates, and evidence.

**[Thesis Point 3 — bold topic header].** 3-5 sentences of supporting detail with specific numbers, dates, and evidence.

### Key Risks

**[Risk 1 — bold topic header].** 2-3 sentences quantifying impact and probability.

**[Risk 2 — bold topic header].** 2-3 sentences quantifying impact and probability.

### Catalysts (Next 12 Months)

| Date | Event | Expected Impact |
|------|-------|----------------|
| YYYY-MM-DD | [Event] | [Impact] |

### What Would Change This Rating

- Upgrade triggers: [specific, measurable conditions]
- Downgrade triggers: [specific, measurable conditions]
```

### Executive Summary Rules

1. Use the **bold-topic paragraph format** for thesis points and risks: `**Bold header.** Detail sentences.`
2. Include the **Rating & Entry Decision** tables — Rating Box + Gate table + Entry Zones consolidated in one place.
3. Include the **Catalysts** table with exact dates.
4. Target length: 500-800 words.
5. **No separate sections**: Do NOT create standalone "Rating & Target Price", "Decision Rules", or "Entry Readiness Assessment" sections. All this information lives here.

---

## Standard Table Templates

Reusable table structures referenced by multiple sections. Adapt column count and labels to the specific company and industry.

### Template A: Multi-Year Financial Summary

Used in §12 Financial Condition and Appendix.

```
|                    | FY20XXA | FY20XXA | FY20XXA | FY20XXE | FY20XXE |
|--------------------|---------|---------|---------|---------|---------|
| Revenue ($M)       |         |         |         |         |         |
| Revenue Growth (%) |         |         |         |         |         |
| Gross Margin (%)   |         |         |         |         |         |
| EBITDA ($M)        |         |         |         |         |         |
| EBITDA Margin (%)  |         |         |         |         |         |
| Net Income ($M)    |         |         |         |         |         |
| FCF ($M)           |         |         |         |         |         |
| FCF Margin (%)     |         |         |         |         |         |
| EPS ($)            |         |         |         |         |         |
Source: Company filings, Data Contract.
```

### Template B: Peer Comparison

Used in §5 Competitive Landscape and §20 Valuation Framework. Do not hard-code columns — select from the two tiers below based on industry and analysis purpose.

**Core Columns** (required):
- Company — standardized name format
- Revenue — scale metric (LTM / quarterly / annual per context)
- Revenue Growth — YoY %
- Gross Profit & Gross Margin — baseline profitability
- EBITDA & EBITDA Margin — operating efficiency

**Optional Columns** (select by industry/purpose):
- Quarterly vs LTM — when seasonality is material, include both
- FCF & FCF Margin — SaaS or capital-intensive businesses
- Net Income — mature profitable companies
- Operating Income — when D&A varies significantly across peers
- CapEx metrics — asset-heavy industries
- Rule of 40 — SaaS-specific (Growth% + Margin%)
- FCF Conversion — earnings quality analysis

```
| Company    | Revenue | Rev Growth | Gross Margin | EBITDA Margin | [Optional...] | Source     | Pull Date |
|------------|---------|------------|--------------|---------------|---------------|------------|-----------|
| {Target}   |         |            |              |               |               | yfinance MCP | YYYY-MM-DD |
| Peer 1     |         |            |              |               |               | yfinance MCP | YYYY-MM-DD |
| Peer 2     |         |            |              |               |               | yfinance MCP | YYYY-MM-DD |
| Peer 3     |         |            |              |               |               | yfinance MCP | YYYY-MM-DD |
| **Median** |         |            |              |               |               | computed    | —          |

Source: All peer data from yfinance MCP / SEC EDGAR MCP on {today's date}. Every row's Pull Date must equal the research day; no historical reuse, no estimation.
```

**Mandatory `Source` and `Pull Date` columns**: every peer row (target + comparables) must include the data origin and the date pulled. `Pull Date` must equal the research day (today). Rows with stale dates, estimation phrasing (`~`, `约`, `approximately`), or missing source are invalid and must be re-fetched before the report is finalized.

**Source-of-truth model**: Template B is a FILTERED VIEW of the Data Contract `## Peer Data` section. The Contract may contain more rows than Template B if §5b or §20a excluded any peer as an outlier — excluded peers must be documented with reason in the relevant "Outlier Exclusions" subsection. **Never remove rows from the Data Contract.** The Contract is append-only and retains every fetched peer as audit record; Template B (the report-level table) reflects only the peers actually used in the analysis.

**Workflow integration**: Template B in §5 (Competitive Landscape) and §20a (Comps) both reference the same `## Peer Data` section of the Data Contract. The section is filled by `data-fetch(mode=supplement)` after §5a Competitor Identification produces the peer set. Subsequent supplement calls during §6-§19 or §20 may append more peer rows on demand. Template B should always reflect the current set of in-use peers (with excluded ones documented separately).

### Template C: DCF Sensitivity

Used in §20 Valuation Framework and Appendix.

```
| WACC \ Terminal Growth | 2.0% | 2.5% | 3.0% | 3.5% | 4.0% |
|------------------------|------|------|------|------|------|
| 8.0%                   |      |      |      |      |      |
| 9.0%                   |      |      |      |      |      |
| 10.0%                  |      |      |      |      |      |
| 11.0%                  |      |      |      |      |      |
| 12.0%                  |      |      |      |      |      |
Source: DCF model. Highlighted cell = base case.
```

---

## Sections 1–21 Writing Requirements

**Section writing order** (enforced by `stock-research` SKILL Steps 4–6):

1. **Step 4 — Analytical sections in numerical order**: §2 → §3 → §4 → §5a (Competitor Identification only) → **[data-fetch supplement: append `## Peer Data` to Contract]** → §5b (Competitive Dynamics + Template B filled from Contract) → §6 → §7 → §8 → §9 → §10 → §11 → §12 → §13 → §14 → §15 → §16 → §17 → §18 → §19.
2. **Step 5 — §20 Valuation**: written AFTER all 18 analytical sections, so DCF/Comps/Reverse DCF assumptions rest on full business understanding rather than financial snapshots alone.
3. **Step 6 — §1 Thesis + §21 Scenarios**: written LAST. They synthesize the entire memo including §20's fair value range. This preserves the Valuation Independence Rule — §20 cannot be retuned to fit a pre-formed thesis.

The final memo file output order is the natural numerical order (§1, §2, ..., §21), but the writing order above ensures dependencies flow correctly: analysis → valuation → narrative.

### Section 1: Thesis Framework
*Purpose — Define conditions that must hold for value creation*

- Summarize in a single clear question the hurdle the investment must clear to create value.
- State 3-5 thesis pillars, each as a specific "if-then" conditional linking business drivers to shareholder value. Each pillar must follow the structured narrative format below.
- Provide a dated, one-sentence "why now" catalyst explaining timing.
- Explain the variant view — the edge versus consensus — and why the market misses it.
- Quantify the variant view gap: compare your fair value estimate with analyst consensus mean target price. State the percentage divergence and explain whether the gap reflects your thesis or a market blind spot.
- Identify the key leading indicator and its critical threshold that would falsify the thesis within two quarters.

**Thesis Pillar Structure** (each pillar must include all 4 components):

```
**Thesis Pillar {N}: {Title}**

**市场机会量化**: 2-3 句描述市场规模、增速、和结构性趋势。以具体 TAM/SAM 数据开头。

**公司捕获逻辑**: 2-3 句解释为什么该公司（而非竞争对手）能够捕获这一机会。
引用竞争优势、设计导入、技术壁垒等。

**财务影响**: 2-3 句量化该 pillar 对收入、利润或估值的具体影响。包含时间线和里程碑。

**Falsification**: {一句话描述什么事实能推翻此 pillar}
```

### Section 2: Market Structure & Size
*Purpose — Quantify addressable opportunity and trajectory*

- Quantify TAM, SAM, and share by product line, customer tier, vertical, and geography.
- Link each major growth driver (regulation, refresh cycle, macro, technology adoption) to quantifiable demand uplift.
- Benchmark current penetration against peer adoption curves to gauge runway.
- Detail scenarios that could shrink SAM within 24 months.
- Explicitly state whether demand or supply is the binding constraint, citing evidence.

### Section 3: Customer Segmentation & Demand
*Purpose — Map who buys and why*

- Segment customer base by size and vertical; identify decision-makers and budget owners.
- Map core workflows, pain points, and mission-criticality to show value dependence.
- Quantify switching costs per segment to assess stickiness.
- Estimate prevalence of "do nothing/build in-house" and why customers still switch.
- Identify key procurement blockers and proof needed to unlock purchase.

### Section 4: Product & Roadmap
*Purpose — Assess product-market fit and durability*

- List core modules and adjacent products; link differentiation to measurable user outcomes.
- Compare product depth vs. breadth against best-of-breed point solutions.
- Describe typical implementation time, required integrations, configurability, and time-to-value.
- Provide quality signals — uptime %, incident frequency, mobile performance — benchmarked against peers.
- Assess roadmap credibility by matching stated milestones to historical delivery.
- Highlight hardest-to-replicate capabilities and their moat (IP, data, process).
- Flag technical debt that could limit scale, reliability, or unit cost within two years.

### Section 5: Competitive Landscape
*Purpose — Position the company*

- Chart direct and indirect competitors by segment and scale.
- Compare pricing, bundling, and feature gaps, including switching friction and contract terms.
- Summarize win/loss reasons from reviews, case studies, and public data.
- Forecast competitor responses and what could neutralize current advantage.
- Flag segments won primarily via channel or regulation rather than product; assess durability.

### Section 6: Ecosystem & Platform Health
*Purpose — Flywheel durability*

- Report API call volume, active developers/apps, SDK adoption, deprecation cadence.
- Quantify marketplace economics — GMV, take rate, rev-share, partner attach rate, concentration.
- Assess partner quality via certifications, lead influence, co-sell efficiency, retention scores.
- Detail governance and trust mechanisms: listing standards, review SLAs, enforcement.
- Evaluate developer experience: documentation quality, sandbox speed, time-to-first-call.
- Define a minimum viable ecosystem health metric and its failure mode.
- State ecosystem-mediated revenue share and top-partner concentration risk.

### Section 7: Go-to-Market & Distribution
*Purpose — Scalability of new-customer engine*

- Decompose demand sources (inbound, outbound, partner, marketplace) and historical mix shift.
- Quantify sales efficiency — ramp time, quota attainment, conversion rates.
- Explain channel and partnership roles (integrations, OEM, platform embed).
- Describe services/CS teams and how training/community become moat.
- Identify the biggest funnel bottleneck and lowest-CAC fix.
- Specify what must change to double leads without doubling opex.

### Section 8: Retention & Expansion
*Purpose — Revenue durability*

- Report gross and net dollar retention by cohort and segment.
- Diagnose churn drivers and timing; visualize churn curve shape if material.
- List expansion vectors — seat growth, module attach, usage attach — ranked by revenue impact.
- Detail contract lengths, renewal mechanics, and price-escalation clauses.
- Synthesize customer interview or review insights to validate retention claims.
- Identify a 60-90 day leading churn indicator and its action trigger.
- Disaggregate expansion into true usage growth vs. price/packaging uplift.

### Section 9: Monetization Model & Revenue Quality
*Purpose — Value capture → durable revenue*

- Map revenue architecture by model (subscription, usage, transaction, etc.) and revenue unit per line.
- Identify price meters and evidence they tie to customer value.
- Show gross and contribution margin by line, plus sensitivity to mix shift.
- Describe revenue-recognition policy, seasonality, deferred revenue, backlog, RPO.
- Quantify revenue visibility and concentration by customer, product, channel, geography.
- Explain exogenous demand drivers that could swing volumes.
- List 2-3 leading KPIs per model that predict revenue 1-2 quarters ahead.
- If payments/credit involved: activity levels, take rate, loss rates, credit/fraud risk bearer.
- Identify the price meter most aligned with value that could scale 10× without churn spike.
- Flag revenue lines with negative optionality or that cannibalize higher-margin lines.

### Section 10: Pricing Power & Elasticity Testing
*Purpose — Value capture*

- Document pricing governance — list vs. realized price, discount-band discipline, price fences.
- Show elasticity evidence from controlled tests, cohort outcomes, win/loss data.
- Summarize willingness-to-pay research, key value drivers, sensitivity by vertical/scale.
- Explain packaging strategy — tiers, bundle attach, usage metering — and value leakage guardrails.
- Provide a log of pricing/packaging changes and realized impact.
- State reference price and switching cost ($/hour) by segment.
- Estimate ARPU ceiling before churn spikes.

### Section 11: Unit Economics & Efficiency
*Purpose — Profitable scale*

- Report CAC, payback period, magic number, and LTV/CAC by segment.
- Show contribution margin by line (software, usage, services).
- Track cohort profitability and cumulative cash contribution over time.
- Quantify implementation, onboarding, and support cost over the lifecycle.
- Identify structurally unprofitable segments and strategy (fix or exit).
- Flag the main constraint blocking 20-30% payback improvement.

### Section 12: Financial Condition
*Purpose — Operations to financial outcomes*

- Decompose revenue mix and component growth, plus gross margin by line.
- Display Rule of 40 score and GAAP-to-cash-flow reconciliation.
- Highlight leading indicators (billings, RPO, backlog).
- Detail SBC, dilution, and share-count trajectory.
- Explain liquidity needs, working-capital position, and FCF breakeven path.
- State milestones and timeline to reach target FCF margin.
- Flag accounting judgments that could swing EBIT by >200 bps.
- Calculate FCF/share CAGR required to reach median fair value; assess plausibility.

- **Key assumptions**: All projection assumptions in this section must follow the Projection Assumptions Format (see Writing Standards) — narrative paragraphs, not parameter lists.

### Section 13: Capital Structure & Cost of Capital
*Purpose — Financing flexibility and risk*

- Detail debt stack — instrument type, fixed/floating mix, hedges, covenants, maturities.
- Quantify leverage and coverage ratios; stress-test higher rates and lower EBITDA.
- Estimate WACC with sensitivity analysis (delegate to `skills/valuation/SKILL.md`).
- Summarize rating-agency stance and triggers.
- Map equity structure — shares, convertibles, buybacks, dividend policy, option/RSU overhang.
- Identify financing shocks that could force strategic pivot or covenant breach.
- State headroom to fund growth at target leverage.
- Define liquidity runway thresholds that force "Sell" or "Await."

### Section 14: Moat & Data Advantage
*Purpose — Defensibility*

- Explain workflow depth and proprietary data that generate lock-in.
- Analyze network or ecosystem effects showing value compounds with scale.
- Demonstrate measurable analytics or AI advantage translating to outcomes.
- Map integration footprint and real switching costs.
- Provide evidence moat is deepening over time, not static or eroding.
- Identify the single event most likely to destroy the moat within two years.

### Section 15: Data & AI Economics
*Purpose — Profit driver*

- Describe data sources underpinning AI: ownership, exclusivity, consent, refresh cadence, quality.
- Quantify labeling/curation cost, training compute cost, inference cost, unit-cost decline roadmap.
- Assess vendor and IP risk — model dependency, portability, open vs. closed source, patents.
- Outline evaluation framework — offline/online testing, attributable KPIs, drift detection, rollback.
- Evaluate data-moat mechanisms — uniqueness, scale, recency, feedback loops.
- Describe self-reinforcing data loops and contractual protections.
- Estimate marginal ROI of each AI feature vs. non-AI baseline.

### Section 16: Execution Quality & Organization
*Purpose — Operating cadence*

- Summarize leadership track record, stability, org design, and succession readiness.
- Report engineering velocity — release cadence, defect and incident rates.
- Triangulate customer sentiment using CSAT, NPS, peer reviews, community signals.
- Assess institutional conviction: report institutional ownership %, top holders (distinguish passive index vs. active managers), and quarter-over-quarter net change. Flag if ownership is unusually low (<30%, potential discovery) or high with recent outflows (crowding risk).
- Flag any single fatal leadership gap in 12-24 months.
- Identify the operational-cadence metric most predictive of misses.

### Section 17: Supply Chain & Operations
*Purpose — Fulfillment and cost risk; include if hardware/services are material*

- List key suppliers, single-source risks, top-five concentration, capacity, lead times, yield.
- Provide field-performance data — warranty, RMA rate, inventory turns, obsolescence reserves.
- Describe logistics/continuity — critical path, 3PL, regional diversification, tariff/export-control risk.
- Explain manufacturing economics — make vs. buy, contract manufacturer terms, learning curve.
- If services material: staffing, utilization, backlog, SLA attainment, margin by tier.
- Identify single points of failure; quantify time/cost to dual source.
- Benchmark cost curve and yield learning rate vs. peers.

### Section 18: Risk Inventory & Mitigations
*Purpose — Explicit downside*

- Prioritize macro, regulatory, competitive, operational, and concentration risks.
- Include payments, credit, or compliance risks if model requires.
- Highlight implementation complexity and time-to-value risk.
- Lead with leading indicators and mitigations; cross-reference §13 and §17.
- Flag the biggest risk in next 12 months, quantify P&L impact, outline recovery plan.
- Define an objective stop-loss or escalation trigger.
- If insider sell/buy ratio (by value) exceeds 5× over 180 days, flag under key-person risk and cross-reference §21 monitoring signals.

### Section 19: M&A Strategy & Optionality
*Purpose — Inorganic growth*

- Review past deals vs. plan — revenue, margin, synergy realization, post-acquisition churn.
- Apply "build-buy-partner" framework with evidence.
- Assess integration capability — playbook, platform convergence, leadership retention.
- Summarize financing mix, valuation discipline, earnout/contingent consideration, impairment history.
- Describe M&A pipeline, regulatory environment, and impact on competitive dynamics.
- Identify capability gap that cannot be closed organically.

### Section 20: Valuation Framework (800-1,200 words)

Delegate to `skills/valuation/SKILL.md` for the full valuation analysis. This section presents five sub-sections:

#### 20a: Comparable Company Analysis
- Peer comp table using Template B with standardized metrics
- **Mandatory statistical summary rows**: Max / 75th Percentile / Median / 25th Percentile / Min for all valuation multiples
- Premium/discount assessment: quantify the percentage premium or discount to peer median for each multiple, with specific justification (e.g., "15% premium to median EV/Revenue justified by 2× faster revenue growth and 800bps higher gross margin")
- Explain outlier peers that significantly skew the statistics

#### 20b: DCF Model
- DCF model with explicit assumptions + sensitivity table (Template C)
- **DCF assumption narrative**: Revenue growth, margin, and CapEx assumptions must follow the Projection Assumptions Format (see Writing Standards).
- **DCF Sanity Check Table** (mandatory — all 5 items must be addressed):

| Sanity Check | Your Model | Acceptable Range | Pass/Fail |
|---|---|---|---|
| Terminal Value % of Total EV | XX% | 50-80% | ✓/✗ |
| Implied Terminal EV/EBITDA | XX.Xx | 8-15x | ✓/✗ |
| WACC vs CAPM Calculation Gap | XXbps | ≤ 100bps | ✓/✗ |
| Y1-Y5 FCF CAGR vs Historical | XX% vs XX% | ≤ 2× historical | ✓/✗ |
| Y5 FCF Margin vs Industry Range | XX% | Within industry range | ✓/✗ |

- If any check fails, explain the rationale for the deviation in a dedicated paragraph

#### 20c: Reverse DCF
- Market-implied growth rate and margin assumptions
- Compare implied assumptions vs your model and management guidance
- State whether the market is pricing in a more optimistic or pessimistic scenario than your base case

#### 20d: Fair Value Synthesis
- Triangulation table with specific methodology weights (must sum to 100%) + 1-sentence justification per weight
- If any method's fair value diverges >30% from the weighted average, include an explanation paragraph
- **Valuation Football Field** (visual range comparison):

```
Valuation Method                Low ────── Range ────── High

DCF Analysis                    $XX ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $XX
Trading Comps                   $XX ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $XX
Reverse DCF (implied)           $XX ▓▓▓▓▓▓▓▓▓▓▓ $XX
                                              ↑
                                    Current Price: $XX
```

- **Scenario Valuation Table**:

| Scenario | Enterprise Value | Equity Value | Price/Share | vs. Current |
|----------|-----------------|-------------|-------------|-------------|
| Bear     | $XXB            | $XXB        | $XX         | -XX%        |
| Base     | $XXB            | $XXB        | $XX         | +XX%        |
| Bull     | $XXB            | $XXB        | $XX         | +XX%        |

- Fair value range (Low/Mid/High) and required margin of safety
- Buy/Trim zones derived from fair value per valuation skill formula
- **Valuation Reconciliation**: If your fair value diverges >30% from current market price, include a dedicated paragraph explaining whether the gap reflects market mispricing, model assumption aggressiveness, or structural factors

#### 20e: Consensus Comparison
- Analyst consensus vs your estimate comparison mini-table:

| | Analyst Consensus | Your Estimate | Delta |
|---|---|---|---|
| Target Price | $XX | $XX | XX% |
| Implied Return | XX% | XX% | XX ppts |
| Rating | X Buy / X Hold / X Sell | {Your Rating} | — |

- Show rating distribution and 3-month trend direction
- If consensus and your valuation diverge by >15%, explain the source of disagreement with specific assumptions that differ
- Key disagreement with market consensus

### Section 21: Scenarios, Catalysts & Monitoring (1,500-2,000 words)

#### 21a: Scenario Analysis (~1,200-1,500 words)

Build 12-24 month bear, base, and bull scenarios summing probabilities to 100%. Each scenario must include all 5 components:

1. **Title + Probability** (e.g., "Bull Case — 25% Probability")

2. **Key Assumptions Table** (mandatory per scenario):

| Assumption | Bull | Base | Bear | vs. Base |
|---|---|---|---|---|
| Revenue CAGR (Y1-Y3) | XX% | XX% | XX% | +/- XX ppts |
| FY{Y}E Revenue ($M) | $XX | $XX | $XX | +/- XX% |
| EBITDA Margin (steady-state) | XX% | XX% | XX% | +/- XX ppts |
| Key product metric | XX | XX | XX | — |
| Market share | XX% | XX% | XX% | +/- XX ppts |

3. **Catalysts Required** (Bull) or **Downside Triggers** (Bear): 3 specific events with timelines

4. **Detailed Rationale**: 200-300 words narrative explaining how the scenario unfolds, with logical chain of events. Each scenario's assumptions must follow the Projection Assumptions Format (see Writing Standards) — not just table values, but narrative paragraphs explaining the logic chain.

5. **Valuation Implications**: DCF-implied price / Comps-implied price / Scenario Target Price

**Bear Case Mandatory Rule**: For stocks with beta ≥ 1.0, bear case total return must be ≥ -20% (cross-reference decision-rules Gate 3). Lead with bear path: bear price/drawdown, recovery path, time to breakeven.

#### 21b: Scenario Comparison (200-300 words)

- **Comparison Table**:

| | Bull | Base | Bear |
|---|---|---|---|
| Probability | XX% | XX% | XX% |
| Target Price | $XX | $XX | $XX |
| Total Return | +XX% | +XX% | -XX% |
| Revenue CAGR | XX% | XX% | XX% |
| EBITDA Margin | XX% | XX% | XX% |
| Key Driver | [1 sentence] | [1 sentence] | [1 sentence] |

- **E[TR] Calculation**: Embed in narrative, not as a raw formula. Example: "预期总回报率为 +34.6%，其中基准情景（50% 概率，+32.7% 回报）贡献 16.4 个百分点..."
- **Path Dependency Analysis**: Identify 2-3 critical inflection points (date + event) where the path forks between scenarios
- Rank expected return per unit downside against two alternative investments

#### 21c: Growth Drivers (800-1,200 words)

Identify 3-5 quantified growth drivers. Each driver (150-250 words) follows this structure:

1. **Opportunity Size**: TAM/SAM with specific dollar amount and growth rate
2. **Timeline with Milestones**: Quarterly or annual milestones for the next 2-3 years
3. **Supporting Data**: 2-3 data points from earnings calls, industry reports, or competitor filings
4. **Bull/Bear Range**: Quantify the upside and downside scenario for this specific driver

#### 21d: Catalysts & Monitoring (~300 words)

- **Catalyst Table**:

| Date | Event | Quantified Impact |
|---|---|---|
| YYYY-MM-DD | [Specific event] | [Revenue/EPS/price impact] |

- **Monitoring Signal Table** ("symptom to action"):

| Signal | Threshold | Action |
|---|---|---|
| [Leading indicator] | [Specific level] | [Buy/Hold/Trim/Sell action] |

- **Insider Trading Monitoring**: Report 180-day buy/sell ratio (by value) and flag cluster buy signals. Exclude routine RSU exercises and 10b5-1 plan sales from sentiment analysis. If net insider selling exceeds 3x buying by value, add to the symptom-action table.
- **Change-My-Mind Triggers**: 3 positive (upgrade) + 3 negative (downgrade) specific, measurable conditions
- Define stop/review level for metric breach or price hitting bear zone

---

## Modeling Notes

- Build revenue model by segment/product; for usage-based, include volume and take-rate drivers.
- Estimate gross margin by line; set opex ratios and SBC; output FCF.
- Provide share count and dilution schedule for next eight quarters (public companies).
- Include two-way sensitivity tables for the two most important drivers.
- Reconcile GAAP operating loss to FCF via clear bridge.

## Appendix Requirements

The Appendix must include the following components:

### Projected Financial Model (5-Year)

This table must be consistent with §20 DCF projections. All figures must come from or reconcile with the Data Contract.

```
| | FY{base}A | FY{+1}E | FY{+2}E | FY{+3}E | FY{+4}E | FY{+5}E |
|---|---|---|---|---|---|---|
| Revenue ($M) | | | | | | |
| Revenue Growth (%) | | | | | | |
| Gross Profit ($M) | | | | | | |
| Gross Margin (%) | | | | | | |
| EBITDA ($M) | | | | | | |
| EBITDA Margin (%) | | | | | | |
| Net Income ($M) | | | | | | |
| CapEx ($M) | | | | | | |
| FCF ($M) | | | | | | |
| FCF Margin (%) | | | | | | |
| EPS ($) | | | | | | |
Source: DCF model, Data Contract. Must reconcile with §20 projections.
```

### Additional Appendix Components
- DCF model detailed assumptions
- Sensitivity tables
- Key assumptions narrative (1,000+ words minimum)
