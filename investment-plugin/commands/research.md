---
description: Generate institutional-grade deep research memo (21 sections + valuation + rating)
argument-hint: "<ticker> [cn/en]"
---

# /research

Generate a comprehensive investment research memorandum for a US-listed stock.

## Usage

```
/research AAPL
/research NVDA cn
/research TSLA en
```

## What This Does

1. Verifies the ticker and detects your language preference
2. Collects financial data from Yahoo Finance, web sources (60+), SEC EDGAR, and FRED
3. Analyzes the company across 21 structured sections
4. Scores business quality (5-dimension Quality Scorecard, 0-100)
5. Values the stock (DCF + Comparable Companies + Reverse DCF)
6. Applies 4 entry gates to produce a Buy/Hold/Await Entry/Sell rating
7. Saves the complete memo to `Research/{ticker}/{date}_memo.md`

## Execution

Read and execute `skills/stock-research/SKILL.md` with:
- `{stock_ticker}` = the ticker provided by the user
- `{output_language}` = "cn" → 中文, "en" → English, or auto-detect from user's message language

## Output

A complete investment memorandum (~8,000-10,000 words) containing:
- Executive Summary with rating and fair value range
- 21 analytical sections with (Fact)/(Analysis)/(Inference) tags
- Quality Scorecard (0-100)
- Decision Rules (4-gate pass/fail)
- Coverage Log (60+ sources)
- Appendix with models and sensitivity tables
