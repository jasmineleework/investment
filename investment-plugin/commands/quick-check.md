---
description: Quick valuation screen (~5 min) to decide if full research is warranted
argument-hint: "<ticker>"
---

# /quick-check

Quick valuation screen for a US- or HK-listed stock. Produces a mini investment memo covering 5 key dimensions to help decide whether a full /research is warranted. Does NOT give a buy/sell rating.

## Usage

```
/quick-check TSLA
/quick-check PLTR
/quick-check 0700.HK
```

## What This Does

1. Detects output language from user's input
2. Fetches key financial data (MCP tools / scripts / WebSearch)
3. Runs full valuation (Comps + DCF + Reverse DCF + Fair Value Synthesis + Buy/Trim Zones)
4. Builds a 5-section mini investment memo:
   - Company Overview & Key Metrics
   - Thesis Framework (if-then pillars + falsification)
   - Full Valuation (Comps, DCF, Reverse DCF, Fair Value Range, Buy/Trim Zones)
   - Scenarios & Catalysts (bear/base/bull + E[TR])
   - Decision Gates (4-gate quick screen)
5. Outputs a structured summary **in the user's language**

## Execution

### Step 0: Language Detection

Detect output language from the user's message:
- Chinese input → `{output_language}` = Chinese; output entire memo in Chinese
- English input → `{output_language}` = English; output entire memo in English
- Other → match the user's language

**This applies to ALL output**: title, section headers, analysis text, and reasoning. Only financial terms, ticker symbols, and proper nouns remain in English.

### Step 1: Data Fetch (Simplified)

Call `skills/data-fetch/SKILL.md` with `{mode}` = "quick":
- Uses MCP tools / Python scripts / WebSearch per the three-tier strategy
- Runs 3-5 additional WebSearch queries for context:
  - `"{ticker} stock analysis {current_year}"`
  - `"{ticker} earnings revenue growth"`
  - `"{ticker} valuation PE EV/EBITDA"`
  - `"{ticker} vs competitors market share"`
  - `"{ticker} risks catalysts outlook"`

### Step 2: Valuation (Full)

Call `skills/valuation/SKILL.md` with all data from Step 1.

This runs the complete three-method valuation:
- **Comparable Company Analysis** — peer group, comp table, implied values, premium/discount
- **DCF** — WACC, 5-year FCF projection, terminal value, sensitivity table
- **Reverse DCF** — market-implied growth, reasonableness check
- **Fair Value Synthesis** — triangulated fair value range (Low / Mid / High), Buy/Trim Zones

All valuation outputs carry forward to Steps 3-5.

### Step 3: Scenario Analysis

Build three scenarios for 12-24 month outlook, anchoring target prices to the Fair Value Range from Step 2.

**Return Derivation** (mechanical — from valuation output):
```
Bull Return = (Fair Value High / Current Price) - 1
Base Return = (Fair Value Mid / Current Price) - 1
Bear Return = (Fair Value Low / Current Price) - 1
```

**Bear Case Floor** (per decision-rules guardrails):
- If beta ≥ 1.0 AND Bear Return > -20%: override Bear Return = -20%, and set Bear Target Price = Current Price × 0.80
- Bear case must be constructed independently (not "base minus a bit")

**Probability Assignment** (default, adjust with evidence):

| Signal | P(Bear) | P(Base) | P(Bull) |
|--------|---------|---------|---------|
| Consensus bullish (>70% Buy) | 20% | 45% | 35% |
| Mixed signals | 25% | 50% | 25% |
| Consensus cautious (<40% Buy) | 35% | 45% | 20% |

**E[TR] Calculation**:
```
E[TR] = P(Bull) × Bull Return + P(Base) × Base Return + P(Bear) × Bear Return
```

**Catalyst Extraction**:
1. Next earnings date from data contract (Earning Dates)
2. Nearest dated event from WebSearch context
3. Each catalyst: specific date, expected impact (quantified), mechanism

### Step 4: Thesis Construction

Synthesize data into a Thesis Framework:
- **Core Investment Question**: one sentence framing the key obstacle
- **3 Thesis Pillars**: each in if-then format with a falsification condition
- **Why Now**: time-sensitive reason with dates
- **Variant View**: how our view differs from consensus
- **Key Leading Indicator**: specific metric + threshold to watch

### Step 5: Decision Gates

Apply 4 quick gates using valuation outputs from Step 2 and scenarios from Step 3:
1. **Expected Return**: E[TR] ≥ 30%
2. **Margin of Safety**: 1 − (Current Price / Fair Value Mid from valuation) ≥ 25%
3. **Skew**: E[TR] / |Bear Return| ≥ 1.7×
4. **Catalyst**: nearest catalyst within 24 months

Count gates passed and provide one-sentence conclusion.

### Step 6: Output

Write the memo **entirely in `{output_language}`**. Template structure:

```markdown
# {ticker} Quick Check | {date}

**{company_name}** ({exchange}: {ticker}) — {one-line description}

---

## 1. Company Overview & Key Metrics

{2-3 句公司简介：主营业务、行业地位、核心驱动力}

| Metric | Value | vs Peers |
|--------|-------|----------|
| Market Cap | $XB | |
| Revenue (FYE) | $XB | YoY +X% |
| Gross Margin | X% | above/below median |
| Operating Margin | X% | |
| EV/EBITDA (TTM) | Xx | premium/discount |
| Forward P/E | Xx | |
| FCF Yield | X% | |
| Net Debt/EBITDA | Xx | |
| 52w Range | $XX - $XX | near high/low |
| Beta | X.X | |

## 2. Thesis Framework

**核心投资问题**：{一句话概括投资必须跨越的核心障碍}

**Thesis Pillars:**

■ **[Pillar 1].** If {条件}, then {价值创造路径}.
  Falsification: {什么事实能推翻这一点}

■ **[Pillar 2].** If {条件}, then {价值创造路径}.
  Falsification: {什么事实能推翻这一点}

■ **[Pillar 3].** If {条件}, then {价值创造路径}.
  Falsification: {什么事实能推翻这一点}

**Why Now**: {为什么现在是关注这只股票的时机，带日期}

**Variant View**: {市场共识是什么，我们的不同看法是什么}

**Key Leading Indicator**: {关键领先指标及其临界阈值}

## 3. Valuation

### Peer Comps

| Company | Ticker | Rev Growth | Gross Margin | Op Margin | EV/Rev | EV/GP | EV/EBITDA | P/E |
|---------|--------|-----------|-------------|-----------|--------|-------|-----------|-----|
| {peer_1} | | | | | | | | |
| {peer_2} | | | | | | | | |
| ... | | | | | | | | |
| **Median** | | | | | | | | |
| **{ticker}** | | | | | | | | |

**Implied Valuation (Comps)**

| Method | Implied Price | vs Current |
|--------|--------------|------------|
| Peer Median EV/Revenue | $XX | +/-XX% |
| Peer Median EV/GP | $XX | +/-XX% |
| Peer Median EV/EBITDA | $XX | +/-XX% |
| Peer Median P/E × FWD EPS | $XX | +/-XX% |

{Premium/discount justification if applicable}

### DCF

**Key Assumptions**: WACC = X.X% | Terminal Growth = X.X% | Projection = 5Y

| Year | Revenue | Growth | EBIT Margin | FCF |
|------|---------|--------|-------------|-----|
| Base | | | | |
| Y1-Y5 | ... | ... | ... | ... |

**DCF Fair Value**: $XX per share

**Sensitivity Table** (Fair Value per share)

| | WACC -1% | WACC Base | WACC +1% |
|---|----------|-----------|----------|
| **Growth +2%** | $XX | $XX | $XX |
| **Growth Base** | $XX | $XX | $XX |
| **Growth -2%** | $XX | $XX | $XX |

### Reverse DCF

- Market-implied revenue CAGR: XX% (vs consensus XX%)
- Market-implied terminal margin: XX%
- Assessment: {reasonable / aggressive / conservative} because {evidence}

### Fair Value Synthesis

| Method | Implied Value | Weight | Notes |
|--------|--------------|--------|-------|
| Comps (Median) | $XX | 35% | Based on X peers |
| DCF (Base Case) | $XX | 40% | WACC=X%, g=Y% |
| Reverse DCF | XX% implied growth | — | Reasonableness check |
| **Weighted Fair Value** | **$XX** | | |

| | Low | Mid | High |
|---|-----|-----|------|
| Fair Value | $XX | $XX | $XX |

**Buy Zone**: $XX – $XX | **Trim Zone**: $XX – $XX | **Current**: ${price}

## 4. Scenarios & Catalysts

### Scenarios (12-24 Months)

| Scenario | Probability | Target Price | Total Return |
|----------|------------|-------------|-------------|
| Bull | XX% | $XX | +XX% |
| Base | XX% | $XX | +/-XX% |
| Bear | XX% | $XX | -XX% |
| **E[TR]** | | | **+/-XX%** |

Bull: {1-2 句描述}
Base: {1-2 句描述}
Bear: {1-2 句描述}

### Catalysts (Next 6-12 Months)

| Date | Event | Potential Impact |
|------|-------|-----------------|
| YYYY-MM | | |

### What Would Change the View

- **Positive triggers**: {具体可量化条件}
- **Negative triggers**: {具体可量化条件}

## 5. Decision Gates

快速检验 4 道投资门槛（不含 Quality Scorecard，留给完整 /research）：

| Gate | Metric | Value | Threshold | Result |
|------|--------|-------|-----------|--------|
| 1. Expected Return | E[TR] | XX% | ≥ 30% | ✓/✗ |
| 2. Margin of Safety | 1-(Price/FV Mid) | XX% | ≥ 25% | ✓/✗ |
| 3. Skew | E[TR]/|Bear Return| | X.X× | ≥ 1.7× | ✓/✗ |
| 4. Catalyst | {nearest catalyst} | {date} | Within 24mo | ✓/✗ |

**Gates Passed: X/4** — {一句话总结：值得深入研究 / 需等待更好入场点 / 风险回报不对称}

注：完整评级（Buy/Hold/Await/Sell）需要 Quality Scorecard，请运行 `/research` 获取。
```

Save to: `Research/{ticker}/{date}_quick-check.md`

## What This Does NOT Include

- Full 21-section analysis
- 60+ source coverage
- Complete Quality Scorecard (0-100)
- Buy/Hold/Sell rating or star rating

For comprehensive analysis, use `/research {ticker}`.
