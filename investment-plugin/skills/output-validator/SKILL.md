---
name: output-validator
description: >
  Pre-output quality gate for investment memos.
  Checks completeness, consistency, and standards compliance
  before the final memo is assembled and saved.
  Called by stock-research after all sections are drafted
  but before final output.
---

# Output Validator

Final quality check before assembling and saving the investment memo. This skill catches structural gaps, inconsistencies, and standards violations.

## When to Run

Called by `stock-research` SKILL.md after:
- All 21 sections are drafted
- Quality Scorecard is computed
- Decision Rules are applied
- Executive Summary is written

But BEFORE the final memo is saved to disk.

---

## Check 1: Structural Completeness

Verify all required components exist:

| Component | Required | Check |
|-----------|----------|-------|
| Executive Summary | ✓ | Contains: Rating, Fair Value Range, E[TR], Buy/Trim Zones, Catalysts, Change Triggers |
| Rating & Target Price | ✓ | Rating is one of: Buy / Hold / Await Entry / Sell |
| Investment Thesis & Variant View | ✓ | Thesis pillars stated, variant view explained |
| Quality Scorecard | ✓ | All 5 dimensions scored, total computed |
| Decision Rules | ✓ | All 4 gates evaluated with Pass/Fail |
| Entry Readiness Assessment | ✓ | Header format present |
| Sections 1-21 | ✓ | All 21 sections present (§17 may be marked N/A if no hardware) |
| Coverage Log | ✓ | Table with source entries |
| Coverage Validator | ✓ | All criteria evaluated |
| Appendix | ✓ | At minimum: DCF model, sensitivity table |

**If any component is missing**: Flag it and draft the missing component before proceeding.

---

## Check 2: Internal Consistency

Cross-check key numbers across sections:

| Check | What to Compare | Action if Mismatch |
|-------|----------------|-------------------|
| Rating vs. Gates | Rating = Buy only if all 4 gates pass + Quality ≥ 70 | Fix rating |
| E[TR] consistency | §21 E[TR] = Executive Summary E[TR] = Decision Rules E[TR] | Reconcile |
| Fair Value consistency | §20 Fair Value Range = Executive Summary range = Decision Rules range | Reconcile |
| Quality Score | Scorecard total = 5 dimension weighted sum × 20 | Recalculate |
| Scenario probabilities | Bull + Base + Bear = 100% | Fix probabilities |
| Buy/Trim Zones | Derived from Fair Value per valuation skill formula | Recalculate |
| Revenue figures | §12 revenue = §9 revenue decomposition total | Reconcile |
| Current price | Same across all sections | Use latest |

**If any inconsistency found**: Resolve by recalculating from the source skill's output, not by averaging.

---

## Check 3: Writing Standards

| Standard | Check | Action if Fail |
|----------|-------|---------------|
| Language | Entire memo in {output_language} | Translate non-conforming sections |
| Section length | Each section 300-600 words | Trim or expand |
| Total length | 8,000-10,000 words | Trim lowest-priority prose |
| Tagging | Every paragraph tagged (Fact)/(Analysis)/(Inference) | Add missing tags |
| Dates | No "recently" or "last quarter" — exact dates only | Replace with dates |
| Calculations shown | Key estimates have visible math | Add calculation steps |
| Acronyms | Expanded on first use | Fix first occurrence |

---

## Check 4: Coverage Quality

Review the Coverage Log and Validator from data-fetch:

| Check | Threshold | Action if Fail |
|-------|-----------|---------------|
| Total unique sources | ≥ 60 | Append Research Methodology Note |
| Quality media | ≥ 10 | Append note |
| Competitor primary | ≥ 5 | Append note |
| Academic/expert | ≥ 5 | Append note |
| Recency | ≥ 60% within 24 months | Append note |
| Domain diversity | ≤ 10% from any single domain | Append note |

If any criterion fails: Do NOT block output. Instead, append a **Research Methodology Note** at the end of the Coverage Validator section stating which criteria fell short and suggesting the user re-run with deeper research mode if available.

---

## Check 5: Risk & Bias Review

| Check | Description |
|-------|-------------|
| Bull bias | Is the rating justified by evidence, or is the analysis overly optimistic? |
| Bear acknowledgment | Are bear-case risks clearly stated with quantified impact? |
| Disconfirming evidence | Has at least one disconfirming source been cited? |
| Assumption transparency | Are key assumptions (growth rate, margin, discount rate) explicitly stated? |
| Conflict check | Do thesis pillars and risk factors logically coexist? |

**If bull bias detected**: Add a prominently placed "Devil's Advocate" paragraph in the Executive Summary.

---

## Output

Return one of:

### ✅ PASS
All checks passed. Proceed to assemble and save the final memo.

### ⚠️ PASS WITH NOTES
Minor issues found (coverage gaps, slight length deviations). List notes to append. Proceed to output.

### ❌ FAIL — REQUIRES FIXES
Critical issues found (missing sections, inconsistent rating, wrong math). List specific fixes required. After fixes, re-run validator.
