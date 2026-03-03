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
