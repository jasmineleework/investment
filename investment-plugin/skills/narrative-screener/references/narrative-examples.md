# Narrative Screener Examples

Two complete examples showing the expected output format for each phase. These are **format templates** — the specific data is illustrative, not real-time analysis.

---

## Example 1: "Data Center Power Demand Doubling"

### Phase 1 Output: `narrative-map.md`

```markdown
## Narrative: 数据中心电力需求翻倍

### 核心驱动力（Drivers）
- Driver 1: AI 训练和推理工作负载指数级增长 → 量化指标: 全球数据中心用电量 CAGR（IEA 预测 2024-2030）
- Driver 2: 云计算和边缘计算持续扩张 → 量化指标: 超大规模数据中心 capex 增速（META/MSFT/AMZN/GOOG）

### 受益链条（Beneficiary Chain）
L1（直接受益）: 电力设备制造商（变压器、配电、UPS）— 数据中心采购电力基础设施
L2（间接受益）: 发电与公用事业（天然气发电、核电、可再生能源）— 电力需求增长推高发电投资
L3（衍生受益）: 冷却系统、稀土/铜材料供应商 — 电力消耗增加带动散热和导电材料需求

### 关键假设（Key Assumptions）
- 假设 1: 如果 AI capex 周期持续 3+ 年，则数据中心电力需求每 4-5 年翻倍 — 验证指标: 超大规模 capex 指引（季度财报）
- 假设 2: 如果电网扩容速度跟不上需求，则电力设备供需缺口扩大、订单积压增长 — 验证指标: 变压器交付周期（行业报告）

### 时间框架
- 短期（0-6月）: 超大规模 Q1-Q2 capex 指引确认，变压器订单持续积压
- 中期（6-18月）: 新数据中心项目进入建设高峰，电力设备营收加速
- 长期（18-36月）: 核电/SMR 项目获批，L2 公用事业受益兑现

### 主题生命周期阶段
[x] 成长期 — 关注度上升，资金流入
判断依据: 数据中心相关 ETF（DTCR）资金持续净流入，分析师覆盖密度上升，但整体估值尚未极端

### 反叙事（Counter-Narrative）
- 失效条件: AI 投资回报不及预期 → 超大规模削减 capex → 电力需求增长放缓
- 受损方: 过度扩产的组件供应商、纯依赖 AI 概念的高估值小盘股
- 拥挤风险: L1 龙头（如 NVDA）已被广泛持有，需关注估值溢价是否过高
```

### Phase 2 Output: `discovery-pool.md`

```markdown
# Discovery Pool: 数据中心电力需求翻倍
**Date**: 2026-03-02 | **Candidates**: 15

## L1 — Direct Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|
| 1 | ETN | Eaton Corp | $135B | 电力管理龙头，数据中心电气基础设施直接受益 |
| 2 | VRT | Vertiv Holdings | $45B | 数据中心关键基础设施（电力/冷却/管理）专业供应商 |
| 3 | PWR | Quanta Services | $48B | 电力基础设施施工龙头，变电站/输电线路建设受益 |
| 4 | EMR | Emerson Electric | $65B | 电力自动化与数据中心管理系统 |
| 5 | HUBB | Hubbell Inc | $22B | 电气组件（变压器、连接器），公用事业和数据中心双重受益 |

## L2 — Indirect Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|
| 6 | VST | Vistra Energy | $42B | 美国最大独立发电商之一，天然气+核电组合受益于电力需求增长 |
| 7 | CEG | Constellation Energy | $75B | 美国最大核电运营商，清洁基荷电力溢价受益 |
| 8 | NRG | NRG Energy | $18B | 发电和零售电力，数据中心PPA需求增长 |
| 9 | SO | Southern Company | $95B | 大型公用事业，数据中心聚集区域电力基础设施投资受益 |

## L3 — Derivative Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|
| 10 | FCX | Freeport-McMoRan | $60B | 铜矿龙头，电力基础设施扩张推高铜需求 |
| 11 | GNRC | Generac Holdings | $9B | 备用发电设备，数据中心冗余电力需求 |
| 12 | AAON | AAON Inc | $8B | 数据中心精密空调系统，电力消耗→散热需求传导 |
| 13 | GEV | GE Vernova | $80B | 燃气轮机和电网设备，发电和输配电双重受益 |
| 14 | SMR | NuScale Power | $3.5B | 小型模块化核反应堆（SMR），长期数据中心电力解决方案 |
| 15 | MP | MP Materials | $4B | 稀土加工，永磁材料用于发电和电力设备 |
```

### Phase 3 Output: `shortlist-ranking.md`

```markdown
# Shortlist Ranking: 数据中心电力需求翻倍
**Date**: 2026-03-02 | **Pool**: 15 → **Shortlisted**: 5

## Ranking

| Rank | Ticker | Company | NarrFit | Fund | SmartMoney | ValDiscount | **Score** | Status |
|------|--------|---------|---------|------|------------|-------------|-----------|--------|
| 1 | ETN | Eaton Corp | 85 | 72 | 78 | 62 | **75.8** | → Phase 4 |
| 2 | VRT | Vertiv | 90 | 80 | 65 | 55 | **75.5** | → Phase 4 |
| 3 | CEG | Constellation | 72 | 68 | 82 | 70 | **72.6** | → Phase 4 |
| 4 | PWR | Quanta Services | 78 | 70 | 60 | 65 | **69.8** | → Phase 4 |
| 5 | HUBB | Hubbell | 75 | 65 | 72 | 60 | **68.9** | → Phase 4 |

## Eliminated

| Ticker | Company | Reason |
|--------|---------|--------|
| SMR | NuScale Power | NarrativeFit 55 — 商业化收入尚未实现，传导确定性低 |
| MP | MP Materials | NarrativeFit 42 — 稀土→电力设备传导链过长 |
| NRG | NRG Energy | Red Flag: CFO 近 60 天卖出 $800K（非计划性） |
| GNRC | Generac | NarrativeFit 52 — 数据中心备用电力仅占小部分收入 |
| AAON | AAON Inc | NarrativeFit 58 — 冷却系统相关但电力暴露度不足 |
| FCX | Freeport | NarrativeFit 48 — 铜价受多重因素影响，narrative 传导弱 |
| SO | Southern Co | Fundamental Score 38 — 收入增速过低（公用事业属性） |
| EMR | Emerson | ValDiscount 22 — 当前估值溢价过高，安全边际不足 |
| VST | Vistra | ValDiscount 18 — P/E 已达历史高位，估值充分 |
| GEV | GE Vernova | ValDiscount 25 — 近期涨幅已 price-in 主题 |
```

### Phase 4 Output: `screening-report.md` (Excerpt — Candidate #1)

```markdown
# 数据中心电力需求翻倍 — 投资筛选报告
**评估日期**: 2026-03-02

---

## 一、投资叙事概览

**主题**: 数据中心电力需求翻倍
**阶段**: 成长期 | **评估日期**: 2026-03-02

### 核心驱动力
- **AI 算力军备竞赛**: 全球超大规模数据中心 capex 在 2025 年超 $2000 亿，AI 训练/推理用电量以每年 30-40% 速度增长（IEA 2025 预测）
- **电网基础设施瓶颈**: 变压器交付周期已从 12 周延长至 50+ 周，供需缺口短期无法缓解

### 受益链条
- **直接受益**: 电力配电/管理设备（变压器、UPS、配电柜）— ETN, VRT, HUBB
- **间接受益**: 发电企业（天然气、核电）— CEG, VST
- **衍生受益**: 电力基础设施施工、冷却系统 — PWR, AAON

### 需要关注的反面信号
- AI 投资回报率不达预期 → 超大规模企业削减 capex → 电力需求增长放缓
- 能源监管收紧（碳排放配额）导致数据中心选址受限

---

## 二、筛选结论与关键发现

| Rank | Ticker | Company | 评级 | 质量评分 | 当前价 | 目标价 | 估值折扣 | 预期三年回报 |
|------|--------|---------|------|---------|--------|--------|---------|------------|
| 1 | ETN | Eaton Corp | **Buy** | 76/100 | $268 | $345 | 28% | 35% |
| 2 | CEG | Constellation Energy | **Hold** | 72/100 | $220 | $265 | 20% | 28% |
| 3 | VRT | Vertiv | **Await** | 74/100 | $118 | $132 | 12% | 18% |
| 4 | PWR | Quanta Services | **Await** | 70/100 | $310 | $365 | 18% | 24% |
| 5 | HUBB | Hubbell | **Hold** | 68/100 | $390 | $460 | 18% | 25% |

### 关键发现

- ETN 是唯一通过全部估值纪律检验的标的，兼具收入增长可见性与合理估值
- 多数候选标的（VRT、PWR）虽然与主题直接相关，但近期股价已大幅上涨，安全边际不足
- 淘汰标的的共同特征：要么与电力主题传导链过长（如稀土 MP），要么估值已充分反映市场预期（如 VST、GEV）

---

## 三、精选标的详评

### ETN — Eaton Corp | Buy

| | |
|---|---|
| **市值** | ~$135B |
| **当前价格** | $268 |
| **目标价格** | $345（$310—$390） |
| **52 周区间** | $215 — $295 |
| **质量评分** | 76 / 100 |

### Investment Thesis

■ **数据中心电气基础设施的不可替代供应商.** Eaton 的电力管理业务直接受益于数据中心建设浪潮——电气部门收入占比约 35%，其中数据中心相关业务在 2025 年增长 22% YoY。变压器和 UPS 系统的订单积压（backlog）达历史新高 $15B，提供长达 18 个月的收入可见性。

■ **结构性供需失衡带来定价权.** 全球电力变压器交付周期从 2022 年的 12 周延长至 2025 年的 50+ 周，Eaton 作为 T1 供应商拥有产能优先分配权。公司已连续 6 个季度提升电气产品均价 5-8%，毛利率从 2023 年的 34% 扩展至 2025 年的 37.5%，定价权护城河清晰。

■ **多终端市场分散风险，非纯 AI 概念股.** 不同于纯数据中心概念股，Eaton 同时受益于美国电网现代化（IIJA 法案 $650B 基建投资）、电动车充电基础设施、工业自动化等多条增长线。即使 AI capex 周期放缓，其他终端市场仍可支撑 10-12% 的有机收入增长。

### 催化剂

■ **Q2 2026 数据中心订单报告（2026 年 7 月）.** 超大规模客户（META、MSFT、AMZN）的 2026 capex 指引将在 Q1/Q2 财报中确认，若维持或上调，将直接验证电力设备需求持续性。

■ **北美电气部门毛利率突破 40%（2026 年底前）.** 管理层指引 2026 年电气部门营业利润率达 24%+，若实现将推动市场重新评估盈利能力。

### 聪明钱动态

■ **内部人看多.** 电气部门 VP 在 90 天内以公开市场价买入 $180K 股票；无关键管理层（CEO/CFO/COO）卖出记录。

■ **机构持续加仓.** Vanguard 持仓环比增加 2.1%，T. Rowe Price 新建仓位；整体机构持股比例维持 82%。分析师 72% 给予买入评级，一致目标价 $330（上行空间 23%）。

### 风险提示

■ **宏观经济衰退.** 若美国经济陷入衰退，非 AI 相关的工业和商业建筑支出可能下滑 15-20%，拖累约 40% 的收入基盘。

■ **原材料成本飙升.** 铜价占电气产品成本约 15-20%，若铜价从当前水平再涨 30%+，可能压缩 200-300bps 毛利率，部分抵消提价效应。

### 行动建议

买入区间：$250-$275 | 减仓区间：$370+
→ `/research ETN` 获取完整深度研报

---

[... 其他标的按同一格式展示 ...]

---

## 四、下一步行动

| 优先级 | 标的 | 行动 |
|--------|------|------|
| 立即 | ETN | `/research ETN` 完整深度研报 |
| 关注 | CEG, HUBB | 设价格提醒：CEG < $200 / HUBB < $370 |
| 定期 | 全部 | 每月检查：超大规模 capex 指引 + 变压器交付周期 |

---

## 附录

### 附录 A: 候选池

{从 discovery-pool.md 嵌入完整表格}

### 附录 B: 评分排序

{从 shortlist-ranking.md 嵌入完整表格}
注：附录中的评分术语保留原始格式，供技术参考。

### 附录 C: 淘汰标的

| Ticker | Company | 淘汰原因 |
|--------|---------|----------|
| SMR | NuScale Power | 与主题关联度不足 — 商业化收入尚未实现，电力需求传导确定性低 |
| MP | MP Materials | 与主题关联度不足 — 稀土→电力设备传导链过长 |
| NRG | NRG Energy | 管理层异常交易 — CFO 近 60 天卖出 $800K（非预设计划） |
| GNRC | Generac | 与主题关联度不足 — 数据中心备用电力仅占极小收入比例 |
| AAON | AAON Inc | 与主题关联度不足 — 冷却系统相关但电力暴露度不足 |
| FCX | Freeport | 与主题关联度不足 — 铜价受多重因素影响，主题传导弱 |
| SO | Southern Co | 基本面偏弱 — 收入增速过低（公用事业属性），增长动能不足 |
| EMR | Emerson | 估值已充分反映 — 当前估值溢价过高，安全边际不足 |
| VST | Vistra | 估值已充分反映 — 市盈率已达历史高位 |
| GEV | GE Vernova | 估值已充分反映 — 近期涨幅已提前消化主题预期 |
```

---

## Example 2: "GLP-1 Weight Loss Drug Revolution"

### Phase 1 Output: `narrative-map.md`

```markdown
## Narrative: GLP-1 减重药革命

### 核心驱动力（Drivers）
- Driver 1: GLP-1 受体激动剂（司美格鲁肽/替尔泊肽）临床疗效远超预期 → 量化指标: 全球 GLP-1 市场规模预测（2025-2030 CAGR）
- Driver 2: 适应症扩展（MASH、心血管、睡眠呼吸暂停）打开天花板 → 量化指标: FDA 批准适应症数量、临床试验管线

### 受益链条（Beneficiary Chain）
L1（直接受益）: GLP-1 药物开发商（Novo Nordisk, Eli Lilly）— 直接销售收入
L2（间接受益）: CDMO/原料药供应商、注射笔/给药设备制造商 — GLP-1 产能扩张受益
L3（衍生受益）: 数字健康/体重管理平台、医疗保险公司（肥胖并发症减少）

### 关键假设（Key Assumptions）
- 假设 1: 如果保险覆盖持续扩大（Medicare Part D 纳入减重），则渗透率加速 — 验证指标: CMS 政策更新、商业保险覆盖率
- 假设 2: 如果口服 GLP-1 疗效不逊于注射剂，则潜在用户群扩大 5-10× — 验证指标: 口服 sema Phase 3 数据（预计 2026 H2）

### 时间框架
- 短期（0-6月）: LLY 口服 GLP-1 数据读出、NVO 产能扩张进展
- 中期（6-18月）: 新适应症 FDA 审批（MASH, 心衰），竞品进入市场（AMGN MariTide）
- 长期（18-36月）: 口服制剂全面上市，第二/三代 GLP-1 管线分化

### 主题生命周期阶段
[x] 成长期 — 关注度上升，资金流入
判断依据: GLP-1 主题 ETF 已成立但 AUM 尚小；sell-side 覆盖密集但 buy-side 分歧犹存（供给瓶颈 vs 竞品侵蚀）

### 反叙事（Counter-Narrative）
- 失效条件: 长期安全性数据出现严重不良反应（甲状腺癌、胰腺炎）→ 黑框警告
- 受损方: 传统减重手术（减重手术器械公司）、垃圾食品公司（需求替代）
- 拥挤风险: NVO/LLY 估值已反映高增长预期，竞品成功可能压缩市占率
```

### Phase 2 Output: `discovery-pool.md`

```markdown
# Discovery Pool: GLP-1 减重药革命
**Date**: 2026-03-02 | **Candidates**: 14

## L1 — Direct Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|
| 1 | NVO | Novo Nordisk (ADR) | $380B | GLP-1 市场开创者，Wegovy/Ozempic 营收主力 |
| 2 | LLY | Eli Lilly | $720B | Mounjaro/Zepbound 增速最快，口服 GLP-1 管线领先 |
| 3 | AMGN | Amgen | $160B | MariTide（次月注射 GLP-1）预计 2026 数据读出 |
| 4 | VKTX | Viking Therapeutics | $8B | VK2735 口服+注射双管线，潜在 best-in-class |

## L2 — Indirect Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|
| 5 | TMO | Thermo Fisher | $190B | CDMO 服务，GLP-1 多肽合成产能扩张受益 |
| 6 | WST | West Pharma | $22B | 注射笔和给药设备组件供应商 |
| 7 | CTLT | Catalent | $18B | 生物制剂 CDMO，GLP-1 灌装产能 |
| 8 | BDX | Becton Dickinson | $65B | 注射针和预灌封注射器，GLP-1 给药耗材 |

## L3 — Derivative Beneficiaries
| # | Ticker | Company | Market Cap | Thesis (1 sentence) |
|---|--------|---------|-----------|---------------------|
| 9 | HIMS | Hims & Hers | $6B | 在线体重管理平台，GLP-1 处方分发 |
| 10 | DOCS | Doximity | $10B | 医生平台，GLP-1 处方教育和市场推广 |
| 11 | GDRX | GoodRx | $3B | 药品折扣平台，GLP-1 高价药物价格比较需求 |
| 12 | ISRG | Intuitive Surgical | $180B | 反向标的监控——减重手术潜在减少（风险确认用） |
| 13 | UNH | UnitedHealth | $450B | 医疗保险，长期受益于肥胖并发症（糖尿病、心血管）减少 |
| 14 | CI | Cigna | $110B | 医疗保险，GLP-1 药费短期冲击 vs 长期并发症节约 |
```

### Phase 3 Output: `shortlist-ranking.md`

```markdown
# Shortlist Ranking: GLP-1 减重药革命
**Date**: 2026-03-02 | **Pool**: 14 → **Shortlisted**: 4

## Ranking

| Rank | Ticker | Company | NarrFit | Fund | SmartMoney | ValDiscount | **Score** | Status |
|------|--------|---------|---------|------|------------|-------------|-----------|--------|
| 1 | NVO | Novo Nordisk | 95 | 82 | 75 | 35 | **75.8** | → Phase 4 |
| 2 | VKTX | Viking Therapeutics | 88 | 55 | 72 | 80 | **75.0** | → Phase 4 |
| 3 | WST | West Pharma | 75 | 70 | 68 | 72 | **71.8** | → Phase 4 |
| 4 | AMGN | Amgen | 70 | 72 | 80 | 60 | **70.5** | → Phase 4 |

## Eliminated

| Ticker | Company | Reason |
|--------|---------|--------|
| LLY | Eli Lilly | ValDiscount 15 — 估值已充分反映 GLP-1 预期（FWD P/E 55×） |
| TMO | Thermo Fisher | NarrativeFit 55 — GLP-1 CDMO 仅占收入 <5% |
| CTLT | Catalent | Red Flag: 3 位分析师 60 天内降级，目标价下调 25% |
| BDX | Becton Dickinson | NarrativeFit 48 — 注射器/针头是通用耗材，GLP-1 占比极小 |
| HIMS | Hims & Hers | Fundamental Score 32 — 盈利能力弱，FCF 为负 |
| DOCS | Doximity | NarrativeFit 40 — 与 GLP-1 的关联过于间接 |
| GDRX | GoodRx | NarrativeFit 38 — 药品折扣平台非直接受益 |
| ISRG | Intuitive Surgical | NarrativeFit 30 — 反向标的，不在正向受益链上 |
| UNH | UnitedHealth | NarrativeFit 45 — 保险收益传导链 >3 步，时间框架过长 |
| CI | Cigna | NarrativeFit 42 — 同上 |
```

### Phase 4 Output: `screening-report.md` (Excerpt — Candidate #1)

```markdown
# GLP-1 减重药革命 — 投资筛选报告
**评估日期**: 2026-03-02

---

## 一、投资叙事概览

**主题**: GLP-1 减重药革命
**阶段**: 成长期 | **评估日期**: 2026-03-02

### 核心驱动力
- **临床疗效远超历史水平**: 司美格鲁肽/替尔泊肽减重幅度达 15-25%（vs 传统药物 5-8%），全球 GLP-1 市场预计 2025-2030 年 CAGR 超 30%
- **适应症爆发式扩展**: 从糖尿病/肥胖延伸至 MASH、心血管、睡眠呼吸暂停，大幅打开潜在市场天花板

### 受益链条
- **直接受益**: GLP-1 药物开发商 — NVO, LLY, AMGN, VKTX
- **间接受益**: CDMO/原料药 + 给药设备供应商 — WST, TMO, CTLT
- **衍生受益**: 数字健康平台、医疗保险公司 — HIMS, UNH

### 需要关注的反面信号
- 长期安全性数据出现严重不良反应（甲状腺癌、胰腺炎）→ 黑框警告
- NVO/LLY 估值已反映高增长预期，竞品成功可能压缩市占率

---

## 二、筛选结论与关键发现

| Rank | Ticker | Company | 评级 | 质量评分 | 当前价 | 目标价 | 估值折扣 | 预期三年回报 |
|------|--------|---------|------|---------|--------|--------|---------|------------|
| 1 | WST | West Pharma | **Buy** | 71/100 | $290 | $380 | 30% | 38% |
| 2 | AMGN | Amgen | **Await** | 78/100 | $295 | $355 | 20% | 28% |
| 3 | VKTX | Viking Therapeutics | **Await** | 62/100 | $68 | $95 | 40% | 45% |
| 4 | NVO | Novo Nordisk | **Hold** | 82/100 | $108 | $125 | 15% | 22% |

### 关键发现

- WST 是唯一通过全部估值纪律检验的标的——受益于 GLP-1 注射笔产能扩张，同时估值尚未被主题炒作推高
- L1 龙头（NVO、LLY）虽然主题关联度最高，但估值已充分反映增长预期，安全边际不足
- 淘汰标的的共同特征：要么与 GLP-1 传导链过长（如 BDX、GDRX），要么基本面尚不支撑（如 HIMS 盈利为负）

---

## 三、精选标的详评

### WST — West Pharmaceutical Services | Buy

| | |
|---|---|
| **市值** | ~$22B |
| **当前价格** | $290 |
| **目标价格** | $380（$340—$420） |
| **52 周区间** | $245 — $320 |
| **质量评分** | 71 / 100 |

### Investment Thesis

■ **GLP-1 注射给药系统的关键零部件供应商.** West Pharma 是全球领先的药物包装和给药系统供应商，其 Daikyo Crystal Zenith® 预灌封注射器组件和自注射笔弹性体密封件被 NVO 和 LLY 的 GLP-1 产品广泛采用。自注射给药系统相关收入约占总收入 25%，且 GLP-1 客户在 2025 年贡献了该板块 40%+ 的增量。

■ **FDA 认证壁垒构成高转换成本护城河.** 药品给药组件需要通过 FDA Container Closure System 认证，替换供应商需 18-24 个月验证周期。West Pharma 与 NVO/LLY 的供应协议平均期限为 5-7 年，客户留存率超 95%。这意味着即使竞品出现，收入锁定期提供显著的可见性。

■ **产能扩张已锁定未来 3 年增长.** 公司在 2024-2025 年投资 $800M 扩建 Kinston（北卡）和 Dublin（爱尔兰）工厂，产能预计在 2026 H2 开始爬坡。管理层指引 2026-2028 年自注射系统板块有机收入增长 12-15% CAGR，高于整体公司 7-9% 的增长指引。

### 催化剂

■ **NVO 产能扩张供应协议公告（2026 年 Q2）.** Novo Nordisk 计划将 Wegovy 产能在 2026 年底前翻倍，West Pharma 作为核心组件供应商预计将获得相应的长期订单增量确认。

■ **口服 GLP-1 数据读出（2026 年 H2）.** 若口服制剂疗效不及注射剂，将进一步巩固注射给药系统的长期需求前景。

### 聪明钱动态

■ **内部人小幅增持.** 一位 Director 在 90 天内以公开市场价买入 $120K 股票；CFO 无交易记录，无异常卖出信号。

■ **机构资金流入.** Wellington Management 持仓环比增加 3.5%，Fidelity 持仓稳定。分析师 65% 给予买入评级，一致目标价 $360（上行空间 24%）。

### 风险提示

■ **口服 GLP-1 替代注射剂.** 若 LLY 口服 GLP-1（orforglipron）数据优异，长期可能减少注射给药需求。口服制剂渗透每增加 10%，West Pharma 自注射板块收入增速可能下降 2-3 个百分点。

■ **原材料与产能爬坡风险.** 弹性体和特种聚合物价格在 2024-2025 年上涨 8-12%，新工厂爬坡期的产能利用率若低于 70%，可能拖累 2026 年毛利率 100-150bps。

### 行动建议

买入区间：$270-$295 | 减仓区间：$400+
→ `/research WST` 获取完整深度研报

---

[... 其他标的按同一格式展示 ...]

---

## 四、下一步行动

| 优先级 | 标的 | 行动 |
|--------|------|------|
| 立即 | WST | `/research WST` 完整深度研报 |
| 关注 | AMGN, VKTX | 设价格提醒：AMGN < $280 / VKTX < $60 |
| 定期 | 全部 | 每月检查：GLP-1 处方量趋势 + 口服制剂临床进展 |

---

## 附录

### 附录 A: 候选池

{从 discovery-pool.md 嵌入完整表格}

### 附录 B: 评分排序

{从 shortlist-ranking.md 嵌入完整表格}
注：附录中的评分术语保留原始格式，供技术参考。

### 附录 C: 淘汰标的

| Ticker | Company | 淘汰原因 |
|--------|---------|----------|
| LLY | Eli Lilly | 估值已充分反映 — 前瞻 P/E 达 55×，GLP-1 增长预期已被市场消化 |
| TMO | Thermo Fisher | 与主题关联度不足 — GLP-1 CDMO 仅占收入不到 5% |
| CTLT | Catalent | 管理层/分析师异常信号 — 3 位分析师 60 天内降级，目标价下调 25% |
| BDX | Becton Dickinson | 与主题关联度不足 — 注射器/针头是通用耗材，GLP-1 占比极小 |
| HIMS | Hims & Hers | 基本面偏弱 — 盈利能力弱，自由现金流为负 |
| DOCS | Doximity | 与主题关联度不足 — 与 GLP-1 的关联过于间接 |
| GDRX | GoodRx | 与主题关联度不足 — 药品折扣平台非直接受益 |
| ISRG | Intuitive Surgical | 与主题关联度不足 — 反向标的，不在正向受益链上 |
| UNH | UnitedHealth | 与主题关联度不足 — 保险收益传导链超过 3 步，时间框架过长 |
| CI | Cigna | 与主题关联度不足 — 同上 |
```

---

## Format Notes

1. **All tables use markdown pipe format** — consistent with investment-plugin style
2. **Scores use integer format** (not decimals) in ranking tables
3. **Language follows user input** — examples shown in Chinese, but English input produces English output
4. **Report is investor-facing** — no internal screening terms (MOS, E[TR], Decision Gates, Gap Index, Skew, Phase 1/2/3/4) in the report body
5. **Each candidate has**: Key Metric Card (5-row table) + 3 ■ Investment Thesis paragraphs + 催化剂 + 聪明钱动态 + 风险提示 + 行动建议
6. **Discovery Pool and Shortlist Ranking** appear only in appendices (附录 A/B), not in the main report body
7. **"行动建议" always points to `/research`** — narrative-screener is a discovery tool, not the final word
