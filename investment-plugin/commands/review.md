---
description: 重新审视已研究标的，生成新研报并与旧版对比
argument-hint: "<ticker>"
---

# /review

Re-evaluate a previously researched stock. Generates a fresh research memo and produces a change-comparison summary against the most recent prior memo.

## Usage

```
/review NVDA
/review AAPL
```

## What This Does

1. Locates the most recent existing memo for the ticker
2. Executes a full `/research` workflow to generate a new memo
3. Compares old vs. new and produces a diff summary

## Execution

### Step 1: Find Previous Memo

Search for the most recent memo file:
```
Glob: {workspace}/Research/{ticker}/*_memo.md
```

Sort by date in filename, take the most recent. If no previous memo exists, inform the user and offer to run `/research` instead.

Read the previous memo and extract:
- Previous rating
- Previous fair value range (Low/Mid/High)
- Previous quality score
- Previous E[TR]
- Previous buy/trim zones
- Previous thesis pillars
- Previous key risks and catalysts

### Step 2: Generate New Memo

Execute full `/research` flow by reading and executing `skills/stock-research/SKILL.md`.

Save new memo as: `Research/{ticker}/{today}_memo.md`

### Step 3: Generate Change Comparison

After the new memo is complete, produce a diff summary:

```markdown
# {ticker} Review Diff | {previous_date} → {today}

## Rating Change
| | Previous | Current | Change |
|---|----------|---------|--------|
| Rating | XX | XX | ↑/↓/→ |
| Quality Score | XX/100 | XX/100 | +X/-X |
| Fair Value (Mid) | $XX | $XX | +X%/-X% |
| E[TR] | XX% | XX% | +Xpp/-Xpp |
| Current Price | $XX | $XX | +X%/-X% |

## Key Financial Changes
| Metric | Previous | Current | Δ |
|--------|----------|---------|---|
| Revenue (TTM) | $XXB | $XXB | +X% |
| Gross Margin | XX% | XX% | +Xpp |
| FCF | $XXB | $XXB | +X% |
| Net Debt | $XXB | $XXB | +X% |

## Thesis Pillar Check
| Pillar | Status | Notes |
|--------|--------|-------|
| [Pillar 1] | ✓ Still valid / ⚠ Weakened / ✗ Invalidated | [brief note] |
| [Pillar 2] | ✓ / ⚠ / ✗ | |
| [Pillar 3] | ✓ / ⚠ / ✗ | |

## New Developments
- [new risk or catalyst not in previous memo]
- [material event since last analysis]

## Removed/Resolved Items
- [risk that has been resolved]
- [catalyst that has passed]

## Gate Changes
| Gate | Previous | Current |
|------|----------|---------|
| 1. E[TR] ≥ 30% | Pass/Fail | Pass/Fail |
| 2. MOS ≥ 25% | Pass/Fail | Pass/Fail |
| 3. Skew ≥ 1.7× | Pass/Fail | Pass/Fail |
| 4. Catalyst | Pass/Fail | Pass/Fail |

## Summary
[2-3 sentences: what changed, why rating changed or didn't, what to watch]
```

Save diff as: `Research/{ticker}/{today}_review-diff.md`

### Output Files

```
Research/{ticker}/
├── {previous_date}_memo.md        # Old memo (untouched)
├── {today}_memo.md                # New memo
└── {today}_review-diff.md         # Change comparison
```
