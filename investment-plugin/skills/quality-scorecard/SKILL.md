---
name: quality-scorecard
description: >
  5-dimension weighted business quality scoring system.
  Produces a 0-100 quality score used by decision-rules
  to determine Buy/Hold/Sell rating. Called by stock-research
  after all 21 sections are drafted.
---

# Quality Scorecard

Score business quality across 5 dimensions. Each dimension is scored 0-5, then weighted to produce a composite score out of 100.

## Inputs

- Analysis content from all 21 sections of the investment memo
- Financial data from data-fetch

## Output

- Composite Quality Score (0-100)
- 5 sub-scores with evidence citations
- Pass/Fail determination (Pass ≥ 70, Sell < 60)

---

## Scoring Framework

### Dimension Weights

| # | Category | Weight | Key Evidence Sections |
|---|----------|--------|----------------------|
| 1 | **Market** | 25% | §2 Market Structure, §3 Customer, §7 GTM |
| 2 | **Moat** | 25% | §5 Competition, §6 Ecosystem, §14 Moat & Data |
| 3 | **Unit Economics** | 20% | §8 Retention, §9 Monetization, §10 Pricing, §11 Unit Econ |
| 4 | **Execution** | 15% | §4 Product, §16 Execution, §19 M&A |
| 5 | **Financial Quality** | 15% | §12 Financial Condition, §13 Capital Structure |

### Scoring Scale (0-5 per dimension)

| Score | Label | Standard |
|-------|-------|----------|
| 5 | Exceptional | Top-decile globally; evidence must be concrete and quantified |
| 4 | Strong | Top-quartile; clear data-backed advantages |
| 3 | Above Average | Better than median; some evidence of edge |
| 2 | Average | In line with peers; no notable advantage or weakness |
| 1 | Below Average | Weaker than peers; identifiable concerns |
| 0 | Poor | Fundamental weakness; red flag |

**Rule: Scores above 3 require explicit, cited evidence.** Do not award 4 or 5 based on narrative alone.

---

## Scoring Criteria by Dimension

### 1. Market (25%)

Evaluate market attractiveness and positioning:

- **TAM trajectory**: Is the addressable market growing, stable, or shrinking?
- **Growth drivers**: Are secular tailwinds durable (regulation, tech adoption, demographic)?
- **Penetration runway**: How much room is left to grow vs. saturation?
- **Demand constraint**: Is demand or supply the binding factor?
- **Customer diversity**: Concentration risk in segments, verticals, geographies?

| Score | Benchmark |
|-------|-----------|
| 5 | TAM growing >15% CAGR, company at <20% penetration, multiple secular tailwinds |
| 4 | TAM growing >10%, clear runway, 1-2 strong tailwinds |
| 3 | TAM growing at GDP+, adequate runway |
| 2 | Mature market, growth roughly GDP-level |
| 1 | Slowing market or high penetration limiting growth |
| 0 | Shrinking TAM or structural demand decline |

### 2. Moat (25%)

Evaluate competitive defensibility:

- **Switching costs**: Quantified cost/effort for customers to leave
- **Network effects**: Does value compound with scale? Evidence?
- **Data advantage**: Proprietary data creating feedback loops
- **Brand/IP**: Patents, regulatory moats, brand pricing power
- **Moat trajectory**: Deepening over time or eroding?

| Score | Benchmark |
|-------|-----------|
| 5 | Multiple reinforcing moats, quantified switching costs >12mo revenue, deepening |
| 4 | Strong moat in 2+ dimensions, evidence of deepening |
| 3 | Meaningful moat in 1 dimension, stable |
| 2 | Some differentiation but not deeply defensible |
| 1 | Weak differentiation, low switching costs |
| 0 | Commodity-like, no defensibility |

### 3. Unit Economics (20%)

Evaluate profitability at the unit level. **Select the benchmark set matching the company's industry type.**

#### Industry Type Detection

Determine the company's primary industry type from the Data Contract (sector/industry fields):

| Industry Type | Examples | Key Metrics |
|--------------|----------|-------------|
| **SaaS / Subscription** | CRM, ADBE, NOW | LTV/CAC, NDR, payback period |
| **Hardware / Semiconductor** | MU, INTC, AMAT | Gross margin cycle, inventory turns, ASP trends |
| **Consumer / Retail** | AMZN, WMT, COST | Same-store growth, inventory turns, GM trajectory |
| **Financial Services** | JPM, V, MA | ROE, efficiency ratio, credit loss rate |
| **Default** | (all others) | Gross margin, operating leverage, contribution margin |

#### Benchmark A — SaaS / Subscription (default if LTV/CAC data is available)

- **LTV/CAC ratio**: >3× good, >5× excellent
- **Payback period**: <18mo good, <12mo excellent
- **Net Dollar Retention**: >110% good, >130% excellent
- **Gross margin**: >60% for software
- **Expansion vectors**: Cross-sell, upsell, usage growth potential

| Score | Benchmark |
|-------|-----------|
| 5 | LTV/CAC >5×, payback <12mo, NDR >130%, expanding margins |
| 4 | LTV/CAC >4×, payback <18mo, NDR >120% |
| 3 | LTV/CAC >3×, payback <24mo, NDR >110% |
| 2 | LTV/CAC 2-3×, payback 24-36mo, NDR 100-110% |
| 1 | LTV/CAC <2×, long payback, NDR <100% |
| 0 | Negative unit economics or unsustainable model |

#### Benchmark B — Hardware / Semiconductor

- **Gross margin** (cycle-adjusted): >40% good, >50% excellent for semis
- **Inventory turns**: >4× good, >6× excellent
- **ASP trend**: Rising or stable = positive; declining under cost pressure = negative
- **Capacity utilization**: >80% good, >90% excellent (but watch over-investment)
- **Capex efficiency**: Revenue per $ capex, improving = positive

| Score | Benchmark |
|-------|-----------|
| 5 | Cycle-adj GM >50%, inv turns >6×, rising ASP, capex ROI improving, dominant cost curve |
| 4 | Cycle-adj GM >45%, inv turns >5×, stable ASP, efficient capex |
| 3 | Cycle-adj GM >40%, inv turns >4×, manageable ASP pressure |
| 2 | Cycle-adj GM 30-40%, inv turns 3-4×, some ASP/inventory concerns |
| 1 | GM <30% or volatile, inv turns <3×, ASP declining, capex heavy |
| 0 | Structurally unprofitable, chronic over-inventory, cost curve disadvantage |

#### Benchmark C — Consumer / Retail

- **Same-store / organic growth**: >5% good, >10% excellent
- **Inventory turns**: >8× good (grocery), >4× (general retail)
- **Gross margin trajectory**: Expanding or stable = positive
- **Customer acquisition efficiency**: Revenue per marketing dollar
- **Unit economics per store/location** (if applicable)

| Score | Benchmark |
|-------|-----------|
| 5 | SSS >10%, inv turns top-quartile, GM expanding, strong unit econ per location |
| 4 | SSS >5%, healthy inv turns, stable GM, efficient customer acquisition |
| 3 | SSS >3%, adequate inv management, GM in line with peers |
| 2 | SSS 0-3%, average inv turns, GM under pressure |
| 1 | SSS negative, inventory problems, GM declining |
| 0 | Structural decline, negative unit economics |

#### Benchmark D — Financial Services

- **ROE**: >15% good, >20% excellent
- **Efficiency ratio**: <60% good, <50% excellent (banks)
- **Credit loss rate**: Below cycle average = positive
- **Fee income ratio**: Higher = more durable (less rate-sensitive)
- **Capital adequacy**: CET1 ratio well above minimums

| Score | Benchmark |
|-------|-----------|
| 5 | ROE >20%, efficiency ratio <50%, credit losses well below avg, strong capital |
| 4 | ROE >15%, efficiency ratio <55%, manageable credit, adequate capital |
| 3 | ROE >12%, efficiency ratio <60%, credit in line with peers |
| 2 | ROE 8-12%, efficiency ratio 60-65%, some credit concerns |
| 1 | ROE <8%, efficiency ratio >65%, rising credit losses |
| 0 | ROE negative, capital concerns, credit crisis |

#### Benchmark E — Default (all other industries)

- **Gross margin**: Above industry median = positive
- **Operating leverage**: EBIT growing faster than revenue = positive
- **Contribution margin by segment**: Identify structurally profitable vs unprofitable
- **Working capital efficiency**: Cash conversion cycle improving
- **Scale economics**: Unit cost declining with volume

| Score | Benchmark |
|-------|-----------|
| 5 | GM top-quartile, strong operating leverage, all segments profitable, improving efficiency |
| 4 | GM above median, positive operating leverage, efficient working capital |
| 3 | GM at median, some operating leverage, adequate efficiency |
| 2 | GM below median, limited operating leverage |
| 1 | GM declining, no operating leverage, working capital strain |
| 0 | Structurally unprofitable at unit level |

### 4. Execution (15%)

Evaluate management and operational capability:

- **Management track record**: Revenue/margin delivery vs. guidance
- **Product velocity**: Release cadence, quality, customer adoption
- **Organizational health**: Turnover, Glassdoor, talent density
- **M&A discipline**: Integration success, value creation vs. destruction
- **Strategic clarity**: Consistent vision, capital allocation logic

| Score | Benchmark |
|-------|-----------|
| 5 | Consistently beats guidance, exceptional product velocity, proven M&A |
| 4 | Mostly beats, strong product, good organizational health |
| 3 | Meets guidance, adequate product cadence |
| 2 | Occasional misses, average execution |
| 1 | Frequent misses, leadership concerns |
| 0 | Material execution failures, management credibility issues |

### 5. Financial Quality (15%)

Evaluate financial strength and trajectory:

- **Rule of 40**: Revenue growth % + FCF margin % (>40% good)
- **FCF conversion**: FCF/Net Income quality
- **Balance sheet**: Net debt/EBITDA, interest coverage, liquidity
- **SBC discipline**: SBC as % of revenue, dilution trajectory
- **Revenue quality**: Recurring %, visibility, deferred revenue trends

| Score | Benchmark |
|-------|-----------|
| 5 | Rule of 40 >60%, FCF positive and growing, net cash, SBC <10% rev |
| 4 | Rule of 40 >40%, FCF positive, manageable debt, SBC <15% rev |
| 3 | Rule of 40 ~40%, near FCF breakeven, adequate liquidity |
| 2 | Rule of 40 <40% but improving, some FCF concerns |
| 1 | Rule of 40 <30%, cash burn, high leverage or SBC |
| 0 | Cash crisis, covenant risk, unsustainable burn |

---

## Calculation

```
Composite Score = (Market × 0.25 + Moat × 0.25 + UnitEcon × 0.20 + Execution × 0.15 + Financial × 0.15) × 20
```

Note: Multiply by 20 to convert 0-5 scale to 0-100.

## Output Format

```markdown
## Quality Scorecard

| Dimension | Score | Weight | Weighted | Key Evidence |
|-----------|-------|--------|----------|--------------|
| Market | X/5 | 25% | X.XX | [brief evidence] |
| Moat | X/5 | 25% | X.XX | [brief evidence] |
| Unit Economics | X/5 | 20% | X.XX | [brief evidence] |
| Execution | X/5 | 15% | X.XX | [brief evidence] |
| Financial Quality | X/5 | 15% | X.XX | [brief evidence] |
| **Total** | | **100%** | **XX/100** | |

**Result**: Pass ✓ / Fail ✗
```

## Decision Thresholds

Read thresholds from `references/markets/{market}.md`:
- Quality Score ≥ {QUALITY_PASS} → eligible for Buy (subject to other gates)
- Quality Score < {QUALITY_SELL} → Sell
- Between {QUALITY_SELL} and {QUALITY_PASS} → Hold or Await Entry
