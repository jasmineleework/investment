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

Evaluate profitability at the customer level:

- **LTV/CAC ratio**: >3× good, >5× excellent
- **Payback period**: <18mo good, <12mo excellent
- **Net Dollar Retention**: >110% good, >130% excellent
- **Gross margin**: >60% for software, benchmark by industry
- **Expansion vectors**: Cross-sell, upsell, usage growth potential

| Score | Benchmark |
|-------|-----------|
| 5 | LTV/CAC >5×, payback <12mo, NDR >130%, expanding margins |
| 4 | LTV/CAC >4×, payback <18mo, NDR >120% |
| 3 | LTV/CAC >3×, payback <24mo, NDR >110% |
| 2 | LTV/CAC 2-3×, payback 24-36mo, NDR 100-110% |
| 1 | LTV/CAC <2×, long payback, NDR <100% |
| 0 | Negative unit economics or unsustainable model |

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
