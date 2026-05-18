# Lessons Learned

<!-- Record patterns and mistakes to avoid repeating them -->

## 2026-03-03: MU 投资备忘录估值膨胀复盘

### 问题描述
0302 full memo 给出 $530 fair value / Buy，而 5 天前的 0225 memo 给出 $398 / Await Entry，0301 quick-check 给出 $265-$443 / 隐含 Hold。基本面零变化，估值差异 100% 来自建模假设。

### 根因

1. **WACC 主观下调**：标准 CAPM 算出 12.2%，以"AI 降低周期性"为由下调至 10.2%。单凭此项 +60% fair value。这是未经周期验证的假设。
2. **两段 DCF 逆向拟合**：第一轮 DCF 得出 EV $129B（远低于市价 $456B），视为"不合理"后切换到第二套参数。这是结果导向建模——用市价反推"合理"折现率。
3. **Bear case 过于宽松**：$380 bear = -4.9% downside，对 beta 1.54 的强周期股毫无意义。直接放大 Skew ratio 至 7.2x，帮助通过 Gate 3。若用 0225 的 $265 bear，Skew = 0.98x，Gate 3 失败。
4. **叙事先行 → 估值跟随**：Phase 2 同时写 §1 Thesis 和 §20 Valuation，bull narrative 形成后 DCF 被调整以匹配叙事。
5. **无跨报告一致性检查**：同一标的两次估值差异 >30%，无机制触发审查。

### 教训规则

- **WACC 纪律**：base case 必须用 raw beta CAPM，不做主观调整。想展示调整后场景可以放在 sensitivity table 的一行里。
- **单模型原则**：一套 DCF 假设产出一个 fair value。禁止"第一套不满意换第二套"。
- **Bear case 地板**：beta > 1 的股票 bear case 至少 -20% drawdown，或引用该行业/该股票的历史最大回撤。
- **估值独立于叙事**：§20 不应与 §1 在同一批次写作。先完成全部定性分析，再独立估值。
- **跨报告 delta check**：如果同一标的 <30 天内有过估值，新报告必须对比并解释差异来源。

---

## 2026-05-19: CRWV 报告 §20a Comps 表 peer 数据由训练记忆估算（用户审计发现）

### 前置背景

PR #4（2026-05-18 合并，"feat: 禁止 peer/估值数据估计纪律写入 SKILL"）已在数据采集层建立通用规则：`valuation/SKILL.md` Step 0 + `data-fetch/SKILL.md` 顶部均强制 "禁止数据估计"。但本次 CRWV 会话因分支基线落后 origin/main 6 个 commits（PR #4/#5 未拉取），完全未感知到 PR #4 的存在，重蹈了同类错误——这是规则已存在但因 git hygiene 失败而被绕过的直接案例。

### 问题描述

CRWV 深度研报 §20a Comparable Companies 表中，**目标股 CRWV 与 NBIS（来自 WebSearch）的数据真实**，但其余 5 个同业（VRT、SMCI、ANET、EQIX、DLR）的市值与营收数据**未经实时 MCP 拉取，仅基于训练数据估算**，导致多项偏差 >20%，其中 VRT 市值估为 $38B，**真实值 $132.7B（偏差 +249%）**。

事后用 yfinance MCP 重新拉取真实数据并重算后，Comps base 由 $137 上修至 $173，加权 fair value 中点由 $101 上修至 $114——虽未改变最终评级（Await Entry，因 DCF base 与 E[TR] 主导），但暴露出工作流的系统性漏洞。

### 根因

1. **数据契约（Data Contract）未覆盖 peer set**：data-fetch SKILL 早期版本强制 target ticker 用 Tier 1 MCP，但对 peer companies 没有等同要求（PR #4 已修正，但本会话基于落后基线工作）。
2. **valuation SKILL 早期版本默认 peer 数据可估算**：§20a 没有"all peer data from real-time source"的硬性 gate（PR #4 已修正，但本会话基于落后基线工作）。
3. **训练记忆的时效幻觉是普遍现象，不限行业**：任何 ticker 在 cutoff 之后的市值、营收、利润都可能与训练快照严重分离（VRT 在本案偏差 +249%，但同类风险存在于所有公司、所有行业）。规则不应分行业——只要是数值字段，无论目标股、peer 还是宏观参数，都必须通过 MCP / 脚本 / 公开披露文件实时抓取并附时间戳。
4. **Phase B Data Reconciliation 缺少数据溯源检查项**：当前 Reconciliation 只检查 target 内部一致性（E[TR]、Fair Value、Quality Score 等），不在校验层强制"每个数值是否有 timestamped source"。
5. **来源标记不明显**：原表用 "~" 前缀（如 "~$38"）表示近似，但读者无法直接识别这是估算而非实测。
6. **git hygiene 缺失**：会话启动时未 `git fetch && git status`，未感知到分支落后，错过 PR #4 已建立的规则。

### 教训规则

- **通用数据溯源规则（行业中立）**：报告中每个数值都必须能在 `data_contract.md` 中找到带时间戳的来源行；"~"、"约"、"approximately"、"市场近似" 等措辞用于数值字段即视为 FAIL，无任何行业例外。**Peer 数据 Pull Date 必须 = 研究当天**——每次研究都重新抓取最新数据，不允许 7 天容忍窗口，不允许复用历史快照，不允许使用训练记忆。任何 ticker、任何行业一视同仁——AI、消费、能源、医药、金融都是同样标准。
- **Phase B 数据溯源审计**：`stock-research/SKILL.md` Step 9 Phase B Reconciliation 加入 "Data Provenance Audit" 校验项，覆盖所有量化字段（目标股、peer、宏观、合同等），作为对 PR #4 上游规则的下游闭环。
- **会话启动 git hygiene**：调用 `/research`、`/quick-check` 或 valuation skill 的会话，**第一步必须 `git fetch && git status`** 确认分支与 origin/main 的 delta；若落后则先 rebase 再开始工作。本次 CRWV 复盘 6 个 commits 落后并重蹈 PR #4 已经禁止的错误，是直接证据。
- **复盘触发标准动作**：用户审计指出数据问题时，必须（a）立即承认，（b）用 MCP 重抓真实值，（c）评估对最终评级的影响，（d）将教训写入 `tasks/lessons.md` 并按需提议 SKILL.md 改动。

### 待改动的 SKILL/流程（本次 PR 已落地）

1. **`investment-plugin/skills/stock-research/SKILL.md` Step 9 Phase B**：新增 "Data Provenance Audit" 校验项，覆盖所有量化字段——本 PR。
2. **`tasks/lessons.md`**：追加本条 2026-05-19 教训——本 PR。

PR #4 已经在 `valuation/SKILL.md` Step 0 与 `data-fetch/SKILL.md` 顶部建立了完整的 "禁止数据估计" 上游规则；本 PR 不再重复，仅在下游 Phase B 加二次校验闭环。

