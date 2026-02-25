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

1. Detects output language from user's input
2. Fetches key financial data via WebSearch (+ optional Yahoo Finance script)
3. Runs a simplified valuation (peer comps + reverse DCF)
4. Provides a preliminary quality assessment (★ 1-5, not full scorecard)
5. Outputs a concise 1-page summary (500-800 words) **in the user's language**

## Execution

### Step 0: Language Detection

Detect output language from the user's message:
- Chinese input → `{output_language}` = Chinese; output entire memo in Chinese
- English input → `{output_language}` = English; output entire memo in English
- Other → match the user's language

**This applies to ALL output**: title, section headers, analysis text, verdict, and reasoning. Only financial terms, ticker symbols, and proper nouns remain in English.

### Step 1: Data Fetch (Simplified)

Call `skills/data-fetch/SKILL.md` with `{mode}` = "quick":
- Runs core WebSearch queries for financial metrics
- Optionally runs Yahoo Finance script if available (non-blocking on failure)
- Runs 3-5 additional WebSearch queries for context:
  - `"{ticker} stock analysis {current_year}"`
  - `"{ticker} earnings revenue growth"`
  - `"{ticker} valuation PE EV/EBITDA"`
  - `"{ticker} vs competitors market share"`
  - `"{ticker} risks catalysts outlook"`

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

Write the memo **entirely in `{output_language}`**. Template structure:

```markdown
# {ticker} Quick Check | {date}

**{company_name}** ({exchange}: {ticker}) — {one-line business description}

---

| {Metric label} | {Value label} |
|--------|-------|
| {Price label} | $XX |
| {Market Cap label} | $XXB |
| P/E (TTM) | XX.X |
| EV/EBITDA | XX.X |
| {Revenue Growth label} (YoY) | XX% |
| {Gross Margin label} | XX% |
| FCF {Margin label} | XX% |
| 52w {Range label} | $XX - $XX |

## {Quick Valuation header}
- {Peer Comps implied range}: $XX - $XX
- {Reverse DCF implied growth}: XX% CAGR
- {Current position}: [{undervalued} / {fair value} / {overvalued}]

## {Preliminary Quality header}: ★★★★☆
[2-3 sentence justification in {output_language}]

## {Key Positives header} (2-3 points)
## {Key Risks header} (2-3 points)

## {Verdict header}: [{Worth Deep Research} / {Pass} / {Wait for Pullback}]
[1-2 sentence reasoning in {output_language}]
```

Save to: `Research/{ticker}/{date}_quick-check.md`

## What This Does NOT Include

- Full 21-section analysis
- 60+ source coverage
- Complete Quality Scorecard (0-100)
- Formal Buy/Hold/Sell rating
- Detailed DCF model

For comprehensive analysis, use `/research {ticker}`.
