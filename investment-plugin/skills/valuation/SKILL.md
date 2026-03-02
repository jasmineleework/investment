---
name: valuation
description: >
  Multi-method equity valuation framework.
  Produces fair value range, buy/trim zones, and market-implied
  expectations via DCF, comparable company analysis, and reverse DCF.
  Called by stock-research for §20 Valuation Framework.
---

# Valuation

Cross-checked valuation using three methods: Comparable Company Analysis, DCF, and Reverse DCF. Outputs a fair value range with buy/trim zones.

## Inputs

- Financial data from data-fetch (quote, financials, cash flow)
- Peer list from §5 Competitive Landscape analysis
- Market config from `references/markets/{market}.md`
- Thresholds from `references/markets/{market}.md`

## Output

- Fair Value Range (Low / Mid / High)
- Buy Zone and Trim Zone
- Market-implied expectations (Reverse DCF)
- Valuation summary table

---

## Method 1: Comparable Company Analysis

### Step 1: Select Peer Group

Select 5-8 comparable companies based on:
- Same or adjacent industry
- Similar business model (revenue type, customer profile)
- Similar scale (within 0.3×-3× revenue)
- Similar growth profile (within ±10pp revenue growth)

### Step 2: Build Comp Table

| Company | Ticker | Rev Growth | Gross Margin | Op Margin | Rule of 40 | EV/Rev | EV/GP | EV/EBITDA | P/E |
|---------|--------|-----------|-------------|-----------|-----------|--------|-------|-----------|-----|
| Peer 1 | | | | | | | | | |
| ... | | | | | | | | | |
| **Median** | | | | | | | | | |
| **{ticker}** | | | | | | | | | |

### Step 3: Derive Implied Value

Apply peer median multiples to {ticker}'s financials:
- EV/Revenue × {ticker} Revenue = Implied EV₁
- EV/Gross Profit × {ticker} GP = Implied EV₂
- EV/EBITDA × {ticker} EBITDA = Implied EV₃
- P/E × {ticker} EPS = Implied Price₄

Convert EV to equity value: Equity = EV - Net Debt
Per-share value = Equity ÷ Shares Outstanding

**Comps Fair Value** = median of implied per-share values

### Step 4: Premium/Discount Justification

If {ticker} deserves a premium or discount to peer median, state why:
- Higher growth → premium justified (quantify: +X% growth → +Y% multiple)
- Lower margins → discount appropriate
- Stronger moat → premium
- Higher risk → discount

---

## Method 2: DCF (Discounted Cash Flow)

### Step 1: Calculate WACC

Use the calc_wacc.py script or calculate manually:

```
Bash: cd {skill_root}/scripts && python3 calc_wacc.py {ticker} --risk-free=RATE --beta=BETA --erp=ERP --debt-rate=RATE --tax-rate=RATE --debt-ratio=RATIO
```

If script unavailable, calculate:
```
Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium
WACC = (E/V) × Cost of Equity + (D/V) × Cost of Debt × (1 - Tax Rate)
```

Default inputs (US market):
- Risk-free rate: 10Y Treasury yield (from data-fetch macro data)
- Equity risk premium: 5.5%
- Beta: from Yahoo Finance quote data
- Tax rate: effective tax rate from financials

**WACC Guardrails** (mandatory):
1. **Raw beta only**: Base case WACC must use the raw beta from the data source (Yahoo Finance). Subjective beta adjustments (e.g., "AI reduces cyclicality") are NOT permitted in the base case.
2. **Adjusted-beta scenario**: If you believe raw beta overstates/understates risk, you may add ONE row to the sensitivity table with adjusted beta and a written justification — but this is a scenario, not the base case.
3. **Terminal growth cap**: Terminal growth rate must be ≤ 3.0% for the base case. Rates above 3.0% require explicit structural evidence (e.g., industry growing at 2× GDP for 20+ years) and may only appear in the bull scenario.
4. **Single model rule**: Produce ONE DCF model with one set of assumptions. Do NOT run a second DCF with different parameters because the first result "seems too low/high". If the DCF fair value diverges significantly from market price, that IS the finding — state it as such. The purpose of DCF is to find YOUR intrinsic value independent of market price, not to reverse-engineer a number that matches the market.

### Step 2: Project Free Cash Flow (5 years)

Build projection from base year FCF:

| Year | Revenue | Growth % | Gross Margin | OpEx % | EBIT | Tax | NOPAT | D&A | CapEx | ΔNWC | FCF |
|------|---------|----------|-------------|--------|------|-----|-------|-----|-------|------|-----|
| Base | | | | | | | | | | | |
| Y1 | | | | | | | | | | | |
| Y2 | | | | | | | | | | | |
| Y3 | | | | | | | | | | | |
| Y4 | | | | | | | | | | | |
| Y5 | | | | | | | | | | | |

Key assumptions to state explicitly:
- Revenue growth rate trajectory (Y1-Y5)
- Margin expansion/compression path
- CapEx intensity
- Working capital changes

### Step 3: Terminal Value

```
Terminal Value = FCF_Y5 × (1 + g) / (WACC - g)
```
- Terminal growth rate (g): 2.5%-3.5% (GDP-level, justify if different)
- Cross-check: Implied terminal EV/EBITDA should be reasonable (8-15×)

### Step 4: Calculate Intrinsic Value

```
Enterprise Value = Σ(FCF_t / (1+WACC)^t) + TV / (1+WACC)^5
Equity Value = EV - Net Debt + Cash
Per Share = Equity Value / Diluted Shares Outstanding
```

### Step 5: Sensitivity Table

Build 2-way sensitivity on the two most impactful drivers:

| | WACC -1% | WACC Base | WACC +1% |
|---|----------|-----------|----------|
| **Growth +2%** | $XX | $XX | $XX |
| **Growth Base** | $XX | $XX | $XX |
| **Growth -2%** | $XX | $XX | $XX |

Use the calc_dcf.py script if available:
```
Bash: cd {skill_root}/scripts && python3 calc_dcf.py --fcf=BASE_FCF --growth=RATES --wacc=RATE --terminal-growth=RATE --net-debt=AMOUNT --shares=COUNT
```

---

## Method 3: Reverse DCF

Determine what the market is pricing in:

### Step 1: Back-solve for implied growth

Given current price → current EV → what FCF growth rate makes DCF = current EV?

```
Find growth rate g such that:
Σ(FCF_base × (1+g)^t / (1+WACC)^t) + TV / (1+WACC)^5 = Current EV
```

### Step 2: Assess reasonableness

- Is implied revenue growth achievable? Compare to consensus and historical
- Is implied margin trajectory realistic?
- What does the market assume about terminal multiple?

### Step 3: State your disagreement

"The market implies X% revenue CAGR and Y% terminal margin. I believe Z% growth and W% margin is more likely because [evidence]."

---

## Fair Value Synthesis

### Triangulate

| Method | Implied Per-Share Value | Weight | Notes |
|--------|------------------------|--------|-------|
| Comps (Median) | $XX | 35% | Based on X peers |
| DCF (Base Case) | $XX | 40% | WACC=X%, g=Y% |
| Reverse DCF Check | $XX implied growth | — | Reasonableness check |
| **Weighted Fair Value** | **$XX** | | |

### Fair Value Range

| | Low | Mid | High |
|---|-----|-----|------|
| Fair Value | $XX | $XX | $XX |
| Source | Bear DCF + Comps low | Weighted median | Bull DCF + Comps high |

### Buy/Trim Zones

Read {MOS_%} from `references/markets/{market}.md`:

```
Buy Zone  = [Fair Value Mid × (1 - {MOS_%} - 10%), Fair Value Mid × (1 - {MOS_%})]
Trim Zone = [Fair Value High, Fair Value High × 1.10]
```

---

## Output Format

Provide all of the above in the output language specified by the calling skill. Include:
1. Comp table
2. DCF model with assumptions
3. Sensitivity table
4. Reverse DCF findings
5. Fair value range + buy/trim zones
6. Key disagreement with market consensus
