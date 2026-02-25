---
name: decision-rules
description: >
  Investment rating decision engine with 4 entry gates.
  Takes outputs from valuation and quality-scorecard skills,
  applies strict thresholds, and produces final Buy/Hold/Await/Sell
  rating with entry plan. Called by stock-research as the final step.
---

# Decision Rules

Apply 4 mandatory entry gates to determine the investment rating. This is the single source of truth for all rating decisions.

## Inputs

- **From valuation skill**: Fair Value Range (Low/Mid/High), Buy/Trim Zones, E[TR] by scenario
- **From quality-scorecard skill**: Composite Quality Score (0-100)
- **From stock-research §21**: Bear/Base/Bull scenarios with probabilities, catalysts with dates
- **Thresholds from** `references/markets/{market}.md`

## Output

- Final Rating: Buy / Hold / Await Entry / Sell
- Gate-by-gate pass/fail table
- Entry Readiness Assessment header
- Action zones with explicit rules

---

## Gate 1: Expected Total Return

### Calculate

```
E[TR] = p_bull × R_bull + p_base × R_base + p_bear × R_bear
```

Include dividends + buybacks in total return calculation.

### Threshold

E[TR] must be ≥ **{HURDLE_TR_%}** (default: 30%) over **{HORIZON}** (default: 24 months).

### Result

| Metric | Value |
|--------|-------|
| Bull Return (p=X%) | +XX% |
| Base Return (p=X%) | +XX% |
| Bear Return (p=X%) | -XX% |
| **E[TR]** | **XX%** |
| Hurdle | {HURDLE_TR_%} |
| **Gate 1** | **Pass ✓ / Fail ✗** |

---

## Gate 2: Margin of Safety

### Calculate

```
Margin of Safety = 1 - (Current Price / Fair Value Mid)
```

### Threshold

MOS must be ≥ **{MOS_%}** (default: 25%).

**Exception**: MOS requirement can be reduced if a near-certain catalyst exists:
- Catalyst probability ≥ 80% (cite source)
- Timeframe ≤ 6 months
- Impact is quantifiable
- In this case, state the adjusted MOS and justification

### Result

| Metric | Value |
|--------|-------|
| Current Price | $XX |
| Fair Value Mid | $XX |
| **Margin of Safety** | **XX%** |
| Required MOS | {MOS_%} |
| Catalyst Exception | Yes/No |
| **Gate 2** | **Pass ✓ / Fail ✗** |

---

## Gate 3: Skew (Return Asymmetry)

### Calculate

```
Skew = E[TR] / |Bear Case Total Return|
```

### Threshold

Skew must be ≥ **{SKEW_X}** (default: 1.7×).

This ensures the expected upside is at least 1.7× the maximum downside. It prevents buying stocks with favorable expected return but catastrophic tail risk.

### Result

| Metric | Value |
|--------|-------|
| E[TR] | +XX% |
| Bear Case Return | -XX% |
| **Skew Ratio** | **X.X×** |
| Required Skew | {SKEW_X} |
| **Gate 3** | **Pass ✓ / Fail ✗** |

---

## Gate 4: "Why Now" (Catalyst)

### Check

At least one dated catalyst or re-rating trigger must exist within **{HORIZON}**.

A valid catalyst must have:
- **Specific date** (or narrow date range, e.g., "Q2 2026 earnings")
- **Quantifiable expected impact** on price, earnings, or multiple
- **Identifiable mechanism** (earnings beat, product launch, regulatory ruling, etc.)

### Result

| Catalyst | Date | Expected Impact | Probability |
|----------|------|----------------|-------------|
| [catalyst 1] | YYYY-MM-DD | [quantified] | XX% |
| [catalyst 2] | YYYY-MM-DD | [quantified] | XX% |

| **Gate 4** | **Pass ✓ / Fail ✗** |

---

## Rating Decision Matrix

```
All 4 Gates Pass + Quality ≥ {QUALITY_PASS}  →  BUY
All 4 Gates Pass + Quality < {QUALITY_PASS}  →  AWAIT ENTRY (quality concern)
1-3 Gates Pass + Quality ≥ {QUALITY_PASS}    →  HOLD or AWAIT ENTRY
Quality < {QUALITY_SELL}                      →  SELL
Fundamental deterioration                     →  SELL
```

### Decision Table

| Gates Passed | Quality Score | Rating |
|-------------|---------------|--------|
| 4/4 | ≥ 70 | **Buy** |
| 4/4 | 60-69 | **Await Entry** |
| 4/4 | < 60 | **Sell** |
| 3/4 | ≥ 70 | **Hold** (state which gate failed) |
| 3/4 | 60-69 | **Hold** |
| 2/4 or less | ≥ 70 | **Await Entry** |
| 2/4 or less | 60-69 | **Await Entry** |
| Any | < 60 | **Sell** |

---

## Entry Readiness Assessment

Output header format:

```
**Quality Score = XX/100 | Entry Price = $XX | Rating = [BUY/HOLD/AWAIT/SELL]**
```

### Action Zones

| Zone | Price Range | Action |
|------|------------|--------|
| Strong Buy | Below Buy Zone low | Full position sizing |
| Buy | Buy Zone | Initiate or add position |
| Hold | Between Buy and Trim | Maintain position |
| Trim | Trim Zone | Reduce position by 25-50% |
| Sell | Above Trim Zone high | Exit position |

### Position Sizing Guidance (if Buy)

- New position: Start at 3-5% of portfolio
- Add on: +1-2% per add, max single position 15-25%
- Scale-in: Buy in 2-3 tranches over 2-4 weeks

---

## Output Summary Table

```markdown
## Rating & Entry Decision

| Gate | Metric | Value | Threshold | Result |
|------|--------|-------|-----------|--------|
| 1. Expected Return | E[TR] | XX% | ≥ 30% | ✓/✗ |
| 2. Margin of Safety | MOS | XX% | ≥ 25% | ✓/✗ |
| 3. Skew | E[TR]/|Bear| | X.X× | ≥ 1.7× | ✓/✗ |
| 4. Catalyst | [name] | [date] | Within 24mo | ✓/✗ |
| Quality | Score | XX/100 | ≥ 70 | ✓/✗ |

**Rating: [BUY / HOLD / AWAIT ENTRY / SELL]**

Buy Zone: $XX - $XX | Trim Zone: $XX - $XX
```

---

## Change-My-Mind Triggers

Always close with:

### 3 Positive Triggers (would upgrade rating)
1. [specific, measurable condition]
2. [specific, measurable condition]
3. [specific, measurable condition]

### 3 Negative Triggers (would downgrade rating)
1. [specific, measurable condition]
2. [specific, measurable condition]
3. [specific, measurable condition]
