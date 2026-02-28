---
description: Quick valuation screen (~5 min) to decide if full research is warranted
argument-hint: "<ticker>"
---

# /quick-check

Quick valuation screen for a US-listed stock. Produces an Executive Summary with peer comps to help decide whether a full /research is warranted. Does NOT give a buy/sell rating.

## Usage

```
/quick-check TSLA
/quick-check PLTR
```

## What This Does

1. Detects output language from user's input
2. Fetches key financial data (MCP tools / scripts / WebSearch)
3. Builds an Executive Summary with thesis points and key risks
4. Runs peer comps (3-5 comparable companies) + reverse DCF
5. Outputs a concise summary (800-1200 words) **in the user's language**

## Execution

### Step 0: Language Detection

Detect output language from the user's message:
- Chinese input → `{output_language}` = Chinese; output entire memo in Chinese
- English input → `{output_language}` = English; output entire memo in English
- Other → match the user's language

**This applies to ALL output**: title, section headers, analysis text, and reasoning. Only financial terms, ticker symbols, and proper nouns remain in English.

### Step 1: Data Fetch (Simplified)

Call `skills/data-fetch/SKILL.md` with `{mode}` = "quick":
- Uses MCP tools / Python scripts / WebSearch per the three-tier strategy
- Runs 3-5 additional WebSearch queries for context:
  - `"{ticker} stock analysis {current_year}"`
  - `"{ticker} earnings revenue growth"`
  - `"{ticker} valuation PE EV/EBITDA"`
  - `"{ticker} vs competitors market share"`
  - `"{ticker} risks catalysts outlook"`

### Step 2: Peer Comps

- Identify 3-5 comparable companies (same sector/industry, similar business model or scale)
- For each peer, collect: Market Cap, EV/Revenue, EV/EBITDA, P/E (FWD), Revenue Growth, Gross Margin, FCF Margin
- Calculate peer median for each metric
- Apply peer median EV/Revenue and EV/EBITDA to {ticker} to derive implied price range
- Run reverse DCF: what revenue growth rate is the market pricing in at current price?

### Step 3: Executive Summary

Synthesize data into an Executive Summary following the ■ bullet format from `references/investment_memo.md`:
- **Investment Thesis**: 3 thesis points, each with a bold header and 2-3 sentences of supporting evidence with specific numbers
- **Key Risks**: 2-3 risks, each with a bold header and 1-2 sentences quantifying impact
- **Catalysts**: upcoming events in the next 6-12 months

**Do NOT assign a buy/sell/hold rating or star rating.** The purpose is to present facts and analysis for the user to decide.

### Step 4: Output

Write the memo **entirely in `{output_language}`**. Template structure:

```markdown
# {ticker} Quick Check | {date}

**{company_name}** ({exchange}: {ticker}) — {one-line business description}

---

## Executive Summary

**Fair Value Range**: ${low} – ${high} | **Current Price**: ${price}

### Key Metrics Snapshot

| Metric | Value | vs Peers |
|--------|-------|----------|
| Market Cap | $XB | |
| Revenue (FYE) | $XM | |
| Revenue Growth (YoY) | X% | above/below median |
| Gross Margin | X% | above/below median |
| EV/EBITDA (FWD) | Xx | premium/discount |
| FCF Yield | X% | above/below median |
| Net Debt/EBITDA | Xx | |
| 52w Range | $XX - $XX | |

### Investment Thesis

■ **[Thesis Point 1 — bold topic header].** 2-3 sentences with specific numbers and evidence.

■ **[Thesis Point 2 — bold topic header].** 2-3 sentences with specific numbers and evidence.

■ **[Thesis Point 3 — bold topic header].** 2-3 sentences with specific numbers and evidence.

### Key Risks

■ **[Risk 1 — bold topic header].** 1-2 sentences quantifying impact.

■ **[Risk 2 — bold topic header].** 1-2 sentences quantifying impact.

---

## Peer Comps

| Metric | {ticker} | {peer_1} | {peer_2} | {peer_3} | Peer Median |
|--------|----------|----------|----------|----------|-------------|
| Market Cap ($B) | | | | | |
| EV/Revenue (FWD) | | | | | |
| EV/EBITDA (FWD) | | | | | |
| P/E (FWD) | | | | | |
| Revenue Growth % | | | | | |
| Gross Margin % | | | | | |
| FCF Margin % | | | | | |

### Implied Valuation

| Method | Implied Price | vs Current |
|--------|--------------|------------|
| Peer EV/Revenue | $XX | +/-XX% |
| Peer EV/EBITDA | $XX | +/-XX% |
| Reverse DCF (implied growth) | XX% CAGR | vs actual XX% |

---

## Catalysts (Next 6-12 Months)

| Date | Event | Potential Impact |
|------|-------|-----------------|
| YYYY-MM | [Event] | [Impact] |

## What Would Change the View

- **Positive triggers**: [specific conditions that would make the stock more attractive]
- **Negative triggers**: [specific conditions that would raise concerns]
```

Save to: `Research/{ticker}/{date}_quick-check.md`

## What This Does NOT Include

- Full 21-section analysis
- 60+ source coverage
- Complete Quality Scorecard (0-100)
- Buy/Hold/Sell rating or star rating
- Detailed DCF model with explicit assumptions
- Entry guidance with price zones

For comprehensive analysis, use `/research {ticker}`.
