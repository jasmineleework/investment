---
description: Discover investment candidates from a narrative theme and rank by valuation gaps
argument-hint: "<narrative description>"
---

# /narrative-screen

Discover stocks from an investment narrative. Decomposes the theme into a beneficiary chain, discovers 10-20 candidates, filters to 3-5 via scoring funnel, then runs full quick-check with smart money signals. Outputs a ranked valuation-gap report.

## Usage

```
/narrative-screen 数据中心电力需求翻倍
/narrative-screen GLP-1 weight loss drug revolution
/narrative-screen AI inference demand shifting to edge devices
```

## What This Does

1. **Narrative Decomposition** (~3 min) — Breaks your theme into: core drivers, beneficiary chain (L1/L2/L3), key assumptions, time horizon, lifecycle stage, counter-narrative
2. **Broad Discovery** (~5 min) — Finds 10-20 candidate stocks via WebSearch, SEC EDGAR, and yfinance
3. **Shortlist Funnel** (~5 min) — Scores on 4 dimensions (Narrative Fit, Fundamentals, Smart Money, Valuation Discount), selects Top 3-5
4. **Full Evaluation** (~10-15 min) — Runs complete quick-check (data-fetch → quality-scorecard → valuation → decision-rules) + smart money deep dive on each finalist
5. **Final Report** — Ranked by valuation gap (MOS% + Quality + Smart Money triple confirmation)

Total time: ~25-30 minutes.

## Output

All files saved to `Research/narratives/{date}_{narrative-slug}/`:

| File | Content |
|------|---------|
| `narrative-map.md` | Structured theme decomposition |
| `discovery-pool.md` | Broad candidate pool (10-20) |
| `shortlist-ranking.md` | Scored ranking + elimination log |
| `screening-report.md` | Final report with ratings per candidate |
| `candidates/{TICKER}/` | Per-ticker: data_contract, quality_score, valuation, decision, smart_money |

## What This Does NOT Include

- Full 21-section research memo (use `/research {ticker}` for deep dive)
- 60+ source coverage per stock
- Historical valuation context beyond 5-year median

For comprehensive analysis on a specific candidate, use `/research {ticker}`.

## Execution

Execute `skills/narrative-screener/SKILL.md` with:
- `{narrative}` = user's input text (everything after `/narrative-screen `)
- Detect `{output_language}` from user's input language
