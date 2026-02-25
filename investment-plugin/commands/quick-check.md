---
description: Quick valuation screen (~5 min) to decide if full research is warranted
argument-hint: "<ticker>"
---

# /quick-check

Quick valuation screen for a US-listed stock. Produces a 1-page summary to help decide whether a full /research is warranted.

## Usage

```
/quick-check TSLA
/quick-check PLTR
```

## What This Does

1. Fetches key financial data (Yahoo Finance only — no full web research)
2. Runs a simplified valuation (peer comps + reverse DCF)
3. Provides a preliminary quality assessment (★ 1-5, not full scorecard)
4. Outputs a concise 1-page summary (500-800 words)

## Execution

### Step 1: Data Fetch (Simplified)

Run Yahoo Finance fetch only:
```
Bash: cd {plugin_root}/scripts && npx tsx yahoo-fetch.ts {ticker}
```

Run 3-5 WebSearch queries for recent news and consensus:
- `"{ticker} stock analysis 2025 2026"`
- `"{ticker} earnings revenue growth"`
- `"{ticker} valuation PE EV/EBITDA"`

### Step 2: Quick Valuation

- Identify 3-5 comparable companies
- Apply peer median EV/Revenue, EV/EBITDA, P/E
- Run reverse DCF: what growth is the market pricing in?
- Derive rough fair value range

### Step 3: Preliminary Quality Assessment

Rate 1-5 stars based on quick scan:
- ★★★★★ Exceptional — clear moat, strong growth, healthy financials
- ★★★★☆ Strong — good fundamentals, minor concerns
- ★★★☆☆ Average — no obvious edge or weakness
- ★★☆☆☆ Below Average — identifiable concerns
- ★☆☆☆☆ Weak — significant red flags

### Step 4: Output

```markdown
# {ticker} Quick Check | {date}

| Metric | Value |
|--------|-------|
| Price | $XX |
| Market Cap | $XXB |
| P/E (TTM) | XX.X |
| EV/EBITDA | XX.X |
| Revenue Growth (YoY) | XX% |
| Gross Margin | XX% |
| FCF Margin | XX% |
| 52w Range | $XX - $XX |

## Quick Valuation
- Peer Comps implied range: $XX - $XX
- Reverse DCF implied growth: XX% CAGR
- Current position: [undervalued / fair value / overvalued]

## Preliminary Quality: ★★★★☆
[2-3 sentence justification]

## Key Positives (2-3 points)
## Key Risks (2-3 points)

## Verdict: [Worth Deep Research / Pass / Wait for Pullback]
[1-2 sentence reasoning]
```

Save to: `Research/{ticker}/{date}_quick-check.md`

## What This Does NOT Include

- Full 21-section analysis
- 60+ source coverage
- Complete Quality Scorecard (0-100)
- Formal Buy/Hold/Sell rating
- Detailed DCF model

For comprehensive analysis, use `/research {ticker}`.
