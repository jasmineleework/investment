# data-fetch MCP 迁移

## SKILL.md 重写
- [x] Step 0: 环境检测从 curl 改为 MCP 工具可用性检测
- [x] Step A1: 新增 Tier 1 MCP 工具调用（yfinance + sec-edgar）
- [x] Step A2: 原脚本降级为 Tier 2 fallback
- [x] Step A3: WebSearch 保留为 Tier 3
- [x] Path B / Step 2-5: 保持不变

## data_contract.md
- [x] 更新来源优先级: SEC EDGAR MCP > Yahoo Finance MCP > Python 脚本 > WebSearch

## 脚本保留
- [x] yahoo_fetch.py — 保留（MCP 无法获取 PE/margins/beta/analyst）
- [x] sec_edgar_fetch.py — 保留（作为 SEC MCP 不可用时的 fallback）
- [x] fred_fetch.py — 保留（无 FRED MCP，唯一自动化来源）

## 验证
- [ ] 运行 /quick-check 确认 MCP 工具被优先调用
- [ ] 检查 Data Contract 填充率
- [ ] 模拟 MCP 不可用确认 fallback 正常
