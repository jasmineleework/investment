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
# Narrative Screening Report: 数据中心电力需求翻倍
**Date**: 2026-03-02 | **Theme Lifecycle**: 成长期 | **Pool**: 15 → **Shortlisted**: 5

---

## Valuation Gap Ranking

| Rank | Ticker | Company | Quality | MOS% | 4-Gate | Smart Money | Rating | Gap Index |
|------|--------|---------|---------|------|--------|-------------|--------|-----------|
| 1 | ETN | Eaton Corp | 76/100 | 28% | 4/4 | 82/100 | **Buy** | ★★★★☆ |
| 2 | CEG | Constellation | 72/100 | 32% | 3/4 | 85/100 | **Hold** | ★★★★☆ |
| 3 | VRT | Vertiv | 74/100 | 18% | 3/4 | 68/100 | **Await** | ★★☆☆☆ |
| 4 | PWR | Quanta Services | 70/100 | 22% | 3/4 | 65/100 | **Await** | ★★★☆☆ |
| 5 | HUBB | Hubbell | 68/100 | 25% | 3/4 | 72/100 | **Hold** | ★★★☆☆ |

---

## Shortlisted Candidates

### #1 ETN — Eaton Corp ★★★★☆ Valuation Gap

**Narrative Benefit Path**:
数据中心电力需求翻倍 → 电力配电和管理设备订单增长 → Eaton ~35% 收入来自电气基础设施直接受益

**Quick-Check Results**:

| Gate | Metric | Value | Threshold | Result |
|------|--------|-------|-----------|--------|
| 1. Expected Return | E[TR] | 35% | ≥ 30% | ✓ |
| 2. Margin of Safety | MOS | 28% | ≥ 25% | ✓ |
| 3. Skew | E[TR]/|Bear| | 1.9× | ≥ 1.7× | ✓ |
| 4. Catalyst | Q2 data center orders report | 2026-07 | Within 24mo | ✓ |
| Quality | Score | 76/100 | ≥ 70 | ✓ |

**Rating: Buy** | Fair Value: $345 | Current: $268

**Smart Money Signals**:
- Analyst: 72% Buy, consensus target $330 (upside 23%)
- Insider: 90-day: VP Electrical bought $180K open market; no key-person selling
- Institutional: Vanguard +2.1% QoQ, BlackRock stable, T. Rowe Price new position

**Key Bull Points**: 数据中心 capex 周期至少延续至 2028; 订单积压提供收入可见性
**Key Risks**: 经济衰退削减非 AI 基建支出; 铜价飙升压缩毛利
**Next Step**: → `/research ETN` for full deep dive

---

[... other candidates follow same format ...]
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

### Phase 4 Output: `screening-report.md` (Final Ranking Excerpt)

```markdown
# Narrative Screening Report: GLP-1 减重药革命
**Date**: 2026-03-02 | **Theme Lifecycle**: 成长期 | **Pool**: 14 → **Shortlisted**: 4

---

## Valuation Gap Ranking

| Rank | Ticker | Company | Quality | MOS% | 4-Gate | Smart Money | Rating | Gap Index |
|------|--------|---------|---------|------|--------|-------------|--------|-----------|
| 1 | WST | West Pharma | 71/100 | 30% | 4/4 | 68/100 | **Buy** | ★★★★☆ |
| 2 | AMGN | Amgen | 78/100 | 22% | 3/4 | 80/100 | **Await** | ★★★☆☆ |
| 3 | VKTX | Viking Therapeutics | 62/100 | 40% | 3/4 | 72/100 | **Await** | ★★☆☆☆ |
| 4 | NVO | Novo Nordisk | 82/100 | 15% | 2/4 | 78/100 | **Hold** | ★★☆☆☆ |

---

## Shortlisted Candidates

### #1 WST — West Pharmaceutical Services ★★★★☆ Valuation Gap

**Narrative Benefit Path**:
GLP-1 减重药革命 → 注射笔/预灌封组件需求激增 → West Pharma ~25% 收入来自自注射给药系统直接受益

**Quick-Check Results**:

| Gate | Metric | Value | Threshold | Result |
|------|--------|-------|-----------|--------|
| 1. Expected Return | E[TR] | 38% | ≥ 30% | ✓ |
| 2. Margin of Safety | MOS | 30% | ≥ 25% | ✓ |
| 3. Skew | E[TR]/|Bear| | 1.8× | ≥ 1.7× | ✓ |
| 4. Catalyst | NVO 产能扩张供应协议公告 | 2026-Q2 | Within 24mo | ✓ |
| Quality | Score | 71/100 | ≥ 70 | ✓ |

**Rating: Buy** | Fair Value: $380 | Current: $290

**Smart Money Signals**:
- Analyst: 65% Buy, consensus target $360 (upside 24%)
- Insider: 90-day: Director bought $120K open market; CFO no activity
- Institutional: Wellington +3.5% QoQ, Fidelity stable

**Key Bull Points**: GLP-1 注射笔需求多年增长可见性; 高转换成本（FDA 组件认证）
**Key Risks**: 口服 GLP-1 成功将减少注射需求; 原材料成本上升压力
**Next Step**: → `/research WST` for full deep dive

---

[... other candidates follow same format ...]
```

---

## Format Notes

1. **All tables use markdown pipe format** — consistent with investment-plugin style
2. **Scores use integer format** (not decimals) in ranking tables
3. **Star ratings** use unicode stars: ★ (filled) and ☆ (empty)
4. **Language follows user input** — examples shown in Chinese, but English input produces English output
5. **Phase 4 candidate sections** follow the same layout as `/quick-check` output (5 key tables + smart money)
6. **"Next Step" always points to `/research`** — narrative-screener is a discovery tool, not the final word
