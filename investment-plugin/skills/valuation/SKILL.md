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

- Financial data from Data Contract (`Research/{ticker}/data_contract.md`)
- Peer list (optional — provided by caller, or constructed internally if not provided):
  - If caller provides a peer list: use it directly
  - If not: select 5-8 peers using Data Contract sector/industry + WebSearch
- Market config from `references/markets/{market}.md`

## Output

- Fair Value Range (Low / Mid / High)
- Buy Zone and Trim Zone
- Market-implied expectations (Reverse DCF)
- Valuation summary table

---

## CRITICAL RULE: No Estimated Data (强制数据真实性)

**所有用于估值的财务数据（财报项、倍数、市值、债务、beta、margin、growth 等）必须来自实时数据源**，绝不允许"市场公开近似值"、"约莫"、"业界常见"、"估计"等措辞。

### 数据来源优先级（严格执行）
1. **Tier 1**: yfinance MCP / SEC EDGAR MCP（实时）
2. **Tier 2**: yahoo_fetch.py / sec_edgar_fetch.py（脚本拉取）
3. **Tier 3**: WebSearch（仅限不可量化的定性分析，**禁止用于数值字段**）

### 禁止行为
- ❌ 在 peer comp 表中填入 "~3.5x"、"约 ~22x" 这类近似值并标注"市场公开近似值"
- ❌ 在缺数据时跳过该 peer 而保留估值结论
- ❌ 使用训练数据中的记忆数值（cutoff 之外的数据必然过时）
- ❌ 在 DCF 输入（WACC、beta、debt rate）中使用估计或"行业平均"代替实测

### 强制行为
- ✅ 每一个数值字段必须能追溯到 data_contract.md 中的具体行
- ✅ Peer 列表中每家公司必须分别调用 MCP / 脚本抓取（与目标股票同样的 data-fetch 流程）
- ✅ 如某 peer 数据缺失，必须用 yahoo_fetch.py `<TICKER>` 显式补抓，**禁止用估计值替代**
- ✅ 若某字段真的无法获取（如非上市公司、私募），必须在表格中标注 `N/A — 数据源不可得`，**不写数字**
- ✅ 报告中每个 peer 数值附近必须能解释来源（脚注或 Data Sources 章节）

### Failure Mode（必须 FAIL 的输出）
- 任何 peer comp 行包含 "~"、"约"、"approximately"、"近似"、"市场公开"、"业界常见" 等措辞
- 任何 valuation table 引用未抓取的数字

---

## Method 1: Comparable Company Analysis

### Step 0: Peer Data Validation（读 Data Contract，不在此抓取）

Peer 数据已由 stock-research Step 4.5 通过 `data-fetch(mode=supplement)`
追加到 Data Contract 的 `## Peer Data` 节。本步骤只做校验，**不发起任何
MCP 调用**——valuation 是消费者，data-fetch 是抓取者，两者职责分离。

执行：

1. 读取 `Research/{ticker}/data_contract.md` 的 `## Peer Data` 节
2. 校验：
   - 至少 5 行（且 ≤ 8 行用于 Comps 中位计算；额外行视为审计保留）
   - 每行 `Pull Date == today`
   - 无 `~`、`约`、`approximately`、`市场近似值` 等估算措辞
3. 运行 validator：
   `python3 investment-plugin/skills/data-fetch/scripts/validate_data_contract.py Research/{ticker}/data_contract.md --mode supplement`
4. 若校验失败：**BLOCK valuation**，返回 stock-research 处理。处理方式有两类：
   - **行数不足或缺关键 peer**：触发 `data-fetch(mode=supplement, peer_set=[NEW])` 增量追加
   - **某行 Pull Date ≠ today**（跨日继续研究）：触发 `data-fetch(mode=supplement, peer_set=[stale_tickers])` 刷新到今日
5. **不允许在 valuation 内部修改 Data Contract**。Data Contract 是 append-only 全集；本 §20a Comps 表是过滤视图——若某行 peer 不可比，
   在 20a "Outlier Exclusions" 段落记录排除原因 + 中位计算时跳过该行；
   **不要删除 Contract 行**。

非美股 peer（如 `SU.PA` Schneider、`6504.T` 三菱）由 data-fetch 通过
yfinance 抓取；本步骤同样只读 Contract、不抓取。

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

Default inputs (from Data Contract → WACC Inputs section):
- Risk-free rate: Data Contract "Risk-Free Rate" field
- Beta: Data Contract "Beta (Raw)" field (WACC guardrail: raw beta only in base case)
- Equity risk premium: Data Contract "Equity Risk Premium" field (default 5.5%)
- Tax rate: Data Contract "Effective Tax Rate" field
- Cost of debt: Data Contract "Pre-Tax Cost of Debt" field
- Debt ratio: derived from Data Contract Balance Sheet (Total Debt / (Total Debt + Market Cap))

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
