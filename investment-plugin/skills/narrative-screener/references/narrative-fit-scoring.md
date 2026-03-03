# Narrative Fit Scoring Reference

Scoring criteria for evaluating how well a candidate stock fits the investment narrative. Used in Phase 3 (shortlist funnel) to eliminate weak-fit candidates.

---

## Formula

```
Narrative Fit Score (0-100) = (Revenue Exposure × 0.35 + Transmission Certainty × 0.25 + Mgmt Intent × 0.20 + Differentiation × 0.20) × 20
```

Each sub-dimension is scored 1-5. Multiply composite by 20 to convert to 0-100 scale.

---

## Sub-Dimensions

### 1. Revenue Exposure (Weight: 35%)

How much of the company's revenue is directly tied to the narrative theme?

| Score | Criteria | Evidence Required |
|-------|----------|-------------------|
| 5 | >50% of revenue directly related | SEC segment data showing majority revenue from theme |
| 4 | 30-50% of revenue related | Segment data or credible analyst breakdown |
| 3 | 15-30% of revenue related | Partial segment match + WebSearch confirmation |
| 2 | 5-15% of revenue related | Indirect exposure via product lines |
| 1 | <5% of revenue related | Tangential connection only |

**Data Sources**:
- `get_segment_data(identifier="{ticker}")` — geographic/product segment breakdown
- WebSearch: `"{ticker} revenue breakdown by segment {narrative keywords}"`
- `get_income_statement(symbol="{ticker}")` — total revenue for denominator

### 2. Transmission Certainty (Weight: 25%)

How direct and reliable is the causal chain from narrative → company revenue?

| Score | Criteria | Example |
|-------|----------|---------|
| 5 | Direct causation, 1-step transmission | Data center buildout → power equipment manufacturer (direct orders) |
| 4 | Clear chain, 2-step transmission | Data center growth → higher electricity demand → utility capex increase |
| 3 | Reasonable inference, logical but multi-step | AI boom → more data centers → more cooling → cooling equipment maker |
| 2 | Indirect, conditional on multiple factors | AI boom → economy grows → consumer spending → retail benefits |
| 1 | Weak association, speculative link | AI boom → general tech optimism → software valuations rise |

**Assessment Method**: LLM reasoning based on narrative map beneficiary chain (L1/L2/L3 classification). L1 candidates typically score 4-5, L2 score 2-4, L3 score 1-3.

### 3. Management Intent (Weight: 20%)

Is the company's management actively positioning to benefit from this narrative?

| Score | Criteria | Evidence Required |
|-------|----------|-------------------|
| 5 | Strategic core — CEO explicitly names this as #1 priority | Earnings call transcript, investor day presentation |
| 4 | Key focus area — significant capex/R&D allocated | Press releases, capex disclosures, product announcements |
| 3 | Active pursuit — mentioned in strategy, some investment | News articles, conference mentions |
| 2 | Follower — reacting to trend, not leading | General industry participation, no proactive moves |
| 1 | Not mentioned — no evidence of management awareness | No relevant mentions in public communications |

**Data Sources**:
- WebSearch: `"{ticker} CEO {narrative keywords} strategy earnings call {current_year}"`
- WebSearch: `"{ticker} capex investment {narrative keywords}"`

### 4. Differentiation (Weight: 20%)

Does the company have a unique competitive advantage within this narrative theme?

| Score | Criteria | Example |
|-------|----------|---------|
| 5 | Clear market leader, dominant position | NVDA in AI chips — >80% data center GPU share |
| 4 | Strong advantage, top-3 player | AMAT in semiconductor equipment — leading in key deposition tools |
| 3 | Comparable to peers, no decisive edge | Multiple cloud providers competing for AI workloads |
| 2 | No advantage, commodity participant | Generic component supplier with many alternatives |
| 1 | Competitive disadvantage, late entrant | Legacy player trying to pivot into theme |

**Assessment Method**: Compare against other candidates in the same L-tier from the discovery pool. Relative positioning matters more than absolute assessment.

---

## Thresholds

| Threshold | Action |
|-----------|--------|
| **Score ≥ 80** | Mark as "Strong Fit" in shortlist ranking |
| **Score 60-79** | Eligible for Phase 4 evaluation |
| **Score < 60** | **Eliminated** — does not enter Phase 4 |

If relaxation needed (< 3 candidates survive): lower threshold to 50, note in output.

---

## Scoring Example

**Narrative**: "Data center power demand doubling"
**Candidate**: Eaton Corp (ETN) — electrical equipment

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Revenue Exposure | 4/5 | ~35% of revenue from electrical infrastructure, data centers are fastest-growing segment |
| Transmission Certainty | 5/5 | Direct: data centers need power distribution → Eaton sells power distribution equipment |
| Mgmt Intent | 4/5 | CEO highlighted data center as strategic priority in Q3 earnings call, increased capex |
| Differentiation | 4/5 | Top-3 in electrical distribution alongside Schneider and ABB, strong US position |

```
NarrativeFit = (4×0.35 + 5×0.25 + 4×0.20 + 4×0.20) × 20
             = (1.40 + 1.25 + 0.80 + 0.80) × 20
             = 4.25 × 20
             = 85 → Strong Fit
```
