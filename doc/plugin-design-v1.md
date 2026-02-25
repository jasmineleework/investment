# Investment Plugin 设计文档 v1

**日期**: 2026-02-25
**状态**: 已确认

---

## 1. 项目定位

个人投资管理 Plugin，支持 Cowork 和 Claude Code 双环境运行。

**Phase 1（当前）**: 美股单只股票深度研究
**Phase 2（后续）**: 多市场支持（港股/台股/韩股）+ Portfolio Manager + Trade Journal + Monitor

核心设计原则：

- **Markdown + JSON 为主**，少量脚本处理 API 调用和数值计算
- **模块化 Skills**，skills 之间可互相引用调用
- **单 Plugin 内部模块化**，而非多个独立 plugin
- **本地文件输出**，不依赖 Obsidian 或其他外部工具

---

## 2. Plugin 目录结构

```
investment-plugin/
├── .claude-plugin/
│   └── plugin.json                 # 插件元数据
├── .mcp.json                       # MCP 数据源配置（预留扩展）
│
├── commands/                       # 斜杠命令（用户入口）
│   ├── research.md                 # /research <ticker>  深度研报
│   ├── quick-check.md              # /quick-check <ticker>  快速估值初筛
│   └── review.md                   # /review <ticker>  定期重新审视 + 变化对比
│
├── skills/                         # 核心能力模块
│   ├── stock-research/             # 深度研报（主 skill）
│   │   └── SKILL.md
│   ├── valuation/                  # 估值计算
│   │   └── SKILL.md
│   ├── quality-scorecard/          # 质量评分卡
│   │   └── SKILL.md
│   ├── data-fetch/                 # 数据获取
│   │   └── SKILL.md
│   └── decision-rules/            # 决策规则引擎
│       └── SKILL.md
│
├── references/                     # 模板与配置
│   ├── investment_memo.md          # 21 章节研报模板（参数化）
│   ├── thresholds.md               # 决策阈值定义
│   ├── markets/                    # 市场配置（预留）
│   │   └── us.md                   # 美股市场参数
│   └── examples/                   # 示例输出（可选）
│       └── memo-example.md
│
├── scripts/                        # 辅助脚本（少量）
│   ├── yahoo-fetch.ts              # Yahoo Finance 数据拉取
│   ├── calc-dcf.ts                 # DCF 模型计算
│   ├── calc-wacc.ts                # WACC 计算
│   └── package.json                # 脚本依赖
│
└── hooks/
    └── hooks.json                  # 事件钩子（预留）
```

---

## 3. 核心文件设计

### 3.1 plugin.json

```json
{
  "name": "investment",
  "version": "0.1.0",
  "description": "个人投资管理插件 — 机构级美股深度研究与投资决策支持",
  "author": {
    "name": "Jasmine"
  },
  "dependencies": []
}
```

### 3.2 .mcp.json（预留）

```json
{
  "mcpServers": {}
}
```

Phase 1 不接入 MCP 数据源。后续可按需添加

---

## 4. Skills 设计

### 4.1 Skills 调用关系

```
commands/research.md
    │
    ▼
skills/stock-research/SKILL.md      ← 主编排 skill
    │
    ├──► skills/data-fetch/SKILL.md        数据采集
    │       └── 调用 scripts/yahoo-fetch.ts
    │
    ├──► skills/quality-scorecard/SKILL.md  质量评分
    │
    ├──► skills/valuation/SKILL.md          估值计算
    │       └── 调用 scripts/calc-dcf.ts
    │       └── 调用 scripts/calc-wacc.ts
    │
    └──► skills/decision-rules/SKILL.md     最终评级
            └── 依赖 quality-scorecard + valuation 输出
```

### 4.2 Skill 间调用机制

通过文本指令引用，Claude 读取后自动加载执行。示例：

```markdown
# stock-research SKILL.md 中的写法：

## 估值分析

读取并执行 `skills/valuation/SKILL.md`，将以下参数传入：
- ticker: {stock_ticker}
- financials: （来自 data-fetch 阶段的财务数据）
- peers: （来自 Section 5 竞争格局分析的可比公司列表）

将估值输出用于 Section 20 和 Executive Summary。
```

### 4.3 各 Skill 职责

| Skill | 职责 | 输入 | 输出 |
|-------|------|------|------|
| **stock-research** | 主编排：环境检测→Ticker确认→调度其他skills→组装21章节报告 | ticker, language | 完整研报 Markdown |
| **data-fetch** | 数据采集：Yahoo Finance API + WebSearch + SEC EDGAR | ticker, market | 结构化财务数据 + 来源列表 |
| **quality-scorecard** | 5维质量评分（Market/Moat/Unit Econ/Execution/Financial） | 各章节分析结果 | 质量分数 0-100 + 各维度得分 |
| **valuation** | DCF + Comps + 逆向DCF + 公允价值区间 | 财务数据, peer list | Fair Value Range, Buy/Trim Zones |
| **decision-rules** | 4道门控检查 → 最终评级 | E[TR], MOS, Skew, Catalysts, Quality Score | Buy/Hold/Await/Sell + Entry Plan |

---

## 5. Commands 设计

### 5.1 /research（完整深度研报）

```markdown
---
description: 生成机构级深度研究备忘录
argument-hint: "<ticker> [语言: cn/en]"
---
```

**完整流程**：

1. 解析 ticker + 语言偏好
2. 调用 `stock-research` skill
3. skill 内部调度 data-fetch → 21 章节分析 → quality-scorecard → valuation → decision-rules
4. 组装完整研报
5. 输出到 `{workspace}/Research/{ticker}/{date}_memo.md`

**生成策略（分批次写作 + 最后组装）**：

```
批次 1（骨架）：数据采集 + 关键章节
  → §1 Thesis Framework
  → §2 Market Structure & Size
  → §12 Financial Condition
  → §13 Capital Structure
  → §20 Valuation Framework
  → §21 Scenarios, Catalysts & Monitoring
  目的：先确立投资论题、财务基础和估值锚点

批次 2（填充）：剩余章节
  → §3-§11（客户、产品、竞争、生态、GTM、留存、商业模式、定价、单位经济）
  → §14-§19（护城河、AI、执行力、供应链、风险、M&A）
  目的：补全公司层面的深度分析

批次 3（总结）：组装 + 最终评级
  → Executive Summary（基于全部章节分析结果）
  → Quality Scorecard（调用 quality-scorecard skill）
  → Decision Rules（调用 decision-rules skill）
  → Entry Readiness Assessment
  → Coverage Log + Validator
  目的：最后写总结，确保评级基于完整分析
```

**风格控制**：
- 每章节 300-600 字，重数据和推理、轻叙述
- 优先用表格和要点，避免冗长段落
- 完整研报目标 8000-10000 字

### 5.2 /quick-check（5 分钟初筛）

```markdown
---
description: 快速估值初筛，决定是否值得深研
argument-hint: "<ticker>"
---
```

**用途**：对一只股票感兴趣但还不确定是否值得做完整研报时，快速看一眼关键指标。

**流程**：data-fetch（简化版）→ valuation（简化版）→ 输出 1 页摘要

**输出内容（约 500-800 字）**：
- 当前价格 / 市值 / 关键财务指标（最近4季度）
- 快速估值：Peer Comps 隐含区间 + 逆向 DCF 隐含增长率
- 初步质量判断（★ 1-5 星，不跑完整评分卡）
- 主要看点 + 主要风险（各 2-3 条）
- 结论：值得深研 / 暂不关注 / 等待回调

**不包含**：21 章节分析、60 源覆盖、完整评分卡

### 5.3 /review（定期重新审视）

```markdown
---
description: 重新审视已研究标的，生成新研报并与旧版对比
argument-hint: "<ticker>"
---
```

**用途**：股票研究已过一段时间，需要检查基本面是否有变化。生成全新研报，同时输出变化对比。

**流程**：
1. 读取最近一份研报（`Research/{ticker}/` 下最新文件）
2. 执行完整 /research 流程，生成新研报
3. 输出 **变化对比摘要**（附在新研报末尾或单独文件）

**变化对比摘要包含**：
- 关键指标变化（价格、估值、财务数据 → 表格对比）
- 评级是否变化 + 变化原因
- 新增/消失的风险或催化剂
- 原 Thesis 各支柱是否仍成立（逐条标注：✓ 仍有效 / ⚠ 弱化 / ✗ 失效）
- Quality Score 变化

**输出文件**：
```
{workspace}/Research/{ticker}/
├── 2026-01-15_memo.md          # 旧研报（保留不动）
├── 2026-02-25_memo.md          # 新研报
└── 2026-02-25_review-diff.md   # 变化对比摘要
```

**注意**：修改已有研报中不满意的部分，不需要使用 /review — 直接在对话中告诉 Claude 哪里要改即可（如 "§20 估值部分 peer 选取有问题，换成 XXX 重算"）。

---

## 6. 数据源架构

### 6.1 Phase 1 数据源

| 层级 | 数据源 | 用途 | 实现方式 |
|------|--------|------|----------|
| L1 | WebSearch / WebFetch | 新闻、分析、行业研究、财报分析 | Claude 内置工具 |
| L2 | Yahoo Finance | 实时报价、财务报表、历史价格、分析师评级 | scripts/yahoo-fetch.ts |
| L3 | SEC EDGAR | 10-K、10-Q、8-K 原始文件 | WebFetch（EDGAR 有免费 API） |
| L4 | FRED | 联邦基金利率、GDP、CPI 等宏观数据 | WebFetch（FRED API 免费） |

### 6.2 数据流

```
data-fetch SKILL.md 执行流程：

1. Yahoo Finance 数据
   └── Bash: npx tsx scripts/yahoo-fetch.ts {ticker}
   └── 输出: quote, financials, historical prices, analyst ratings

2. WebSearch 信息源（目标 60+ 独立来源）
   ├── 财报与 IR："{ticker} earnings transcript 2025"
   ├── 行业分析："{ticker} industry outlook TAM"
   ├── 竞争格局："{ticker} vs competitors market share"
   ├── 风险因素："{ticker} risks challenges headwinds"
   ├── 管理层："{ticker} CEO management strategy"
   └── ... (按 21 章节需求编排查询)

3. SEC EDGAR（如适用）
   └── WebFetch: EDGAR full-text search API

4. 覆盖度验证
   └── 执行 Coverage Validator（60源阈值检查）
```

---

## 7. 输出规格

### 7.1 文件输出

```
{workspace}/Research/{ticker}/
├── {date}_memo.md              # 完整研报
├── {date}_quick-check.md       # 快速检查（如有）
└── _history.md                 # 该标的研究历史索引
```

### 7.2 研报结构（与现有 investment_memo.md 一致）

```
Executive Summary
├── Rating | Fair Value Range | Expected Return
├── Buy/Trim Zones | Catalysts
└── What Would Change Rating

Rating & Target Price

Investment Thesis & Variant View

Decision Rules / Quality Scorecard / Entry Assessment

Sections 1-21（完整章节）

Coverage Log + Coverage Validator

Appendix（模型、数据表、假设）
```

### 7.3 参数化模板

模板中的变量：

| 变量 | 默认值（美股） | 说明 |
|------|----------------|------|
| {stock_name} | — | 公司全称 |
| {stock_ticker} | — | 股票代码 |
| {output_language} | 用户语言 | 输出语言 |
| {market} | US | 市场标识 |
| {benchmark} | S&P 500 | 基准指数 |
| {currency} | USD | 货币 |
| {MOS_%} | 25% | 安全边际 |
| {SKEW_X} | 1.7× | 收益/回撤比 |
| {QUALITY_PASS} | 70 | 质量分及格线 |
| {QUALITY_SELL} | 60 | 质量分卖出线 |
| {HURDLE_TR_%} | 30% | 预期回报门槛 |
| {HORIZON} | 24 months | 决策周期 |

---

## 8. 环境兼容

### 8.1 Cowork 模式

- Skills 通过 Cowork 的 skill 加载机制自动识别
- 输出文件写入 Cowork workspace 文件夹
- 用户通过自然语言触发（"帮我分析 AAPL"）

### 8.2 Claude Code 模式

- 通过 `claude plugin install` 安装
- 支持 `/research AAPL` 斜杠命令触发
- 输出文件写入当前工作目录下 `Research/` 文件夹
- scripts 通过 Bash 工具执行

### 8.3 环境检测（stock-research SKILL.md 内置）

```
检测顺序：
1. 检查是否有 deep_research 工具 → 使用深度研究
2. 检查是否有 Bash/Edit/Write → Claude Code / Cowork 环境
3. 检查是否有 artifacts/analysis_tool → claude.ai 网页
4. 回退 → WebSearch 迭代模式
```

---

## 9. 多市场扩展路径（Phase 2 预留）

当前架构已预留扩展点：

```
references/markets/
├── us.md       ← Phase 1 实现
├── hk.md       ← Phase 2
├── tw.md       ← Phase 2
└── kr.md       ← Phase 2
```

每个市场配置文件定义：交易所、Ticker格式、货币、会计准则、监管披露源、基准指数、市场特有风险项。

stock-research SKILL.md 在 Step 2 识别市场后，加载对应 market profile，注入模板参数。

**21 章节框架不需要为每个市场维护单独版本** — 通过条件注入处理差异（约 5-6 个章节需要市场感知的补充段落）。

---

## 10. Phase 1 实施计划

| 步骤 | 内容 | 优先级 |
|------|------|--------|
| 1 | 创建 plugin 骨架目录 + plugin.json | P0 |
| 2 | 编写 stock-research SKILL.md（主编排） | P0 |
| 3 | 编写 data-fetch SKILL.md + yahoo-fetch.ts | P0 |
| 4 | 迁移 investment_memo.md 到 references/（参数化） | P0 |
| 5 | 编写 quality-scorecard SKILL.md | P0 |
| 6 | 编写 valuation SKILL.md + calc-dcf.ts / calc-wacc.ts | P0 |
| 7 | 编写 decision-rules SKILL.md | P0 |
| 8 | 编写 commands/research.md | P0 |
| 9 | 编写 commands/quick-check.md + review.md | P1 |
| 10 | 端到端测试（选一只股票完整跑一遍） | P0 |
| 11 | references/markets/us.md 市场配置 | P1 |
| 12 | 编写 thresholds.md 独立配置 | P1 |

---

## 11. 与现有 stock-research skill 的关系

当前 Cowork 中已安装的 `stock-research` skill 是单文件 skill。新 plugin 是它的完整升级版：

| 维度 | 现有 skill | 新 plugin |
|------|-----------|-----------|
| 结构 | 单个 SKILL.md | 多 skill + commands + scripts |
| 估值 | 全部内联在一个 prompt 中 | 独立 valuation skill，可复用 |
| 数据 | 纯 WebSearch | WebSearch + Yahoo Finance API + SEC EDGAR |
| 评分 | 内联在模板中 | 独立 quality-scorecard skill |
| 扩展性 | 低 | 高（模块化，可加 portfolio/monitor 等） |
| 多市场 | 仅美股 | 架构预留，Phase 2 扩展 |

迁移完成后，旧 skill 可以退役。

---

_文档版本: v1.0_
_最后更新: 2026-02-25_
