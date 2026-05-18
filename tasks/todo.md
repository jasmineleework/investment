# moomoo SG 账号对接 — 从 0 搭建到 portfolio 分析

> 目标：让 investment-plugin 能拉到用户 moomoo SG 账号的实时持仓 + 行情，作为 portfolio 分析的输入。

---

## Phase A — 本地环境就绪（一次性）

用户视角：装两个东西（一个 GUI 应用 + 一个 Python 库），登录 SG 账号，跑一行 verify 命令看到"连接成功"。

- [ ] **A1. 安装 moomoo OpenD GUI（macOS）**
  - 用户看到：桌面 / Applications 出现 `moomoo OpenD` 应用，可启动
  - 我做：从官方源下载最新版 tar.gz → 解压 → 复制 .app 到 /Applications/
  - 用户做：首次启动如遇"未验证开发者"提示，到「系统设置 → 隐私与安全性」点「仍要打开」
  - 验收：`ls /Applications/ | grep -i opend` 有返回，双击能起来

- [ ] **A2. 在 OpenD GUI 内登录 moomoo SG 账号**
  - 用户看到：GUI 左侧填账号密码 → 完成风险测评 → 看到"行情登录成功"+"交易登录成功"两个绿点
  - 用户做：自己登录（不通过 SDK，账号密码我不接触）
  - 监听地址保持默认：`127.0.0.1:11111`
  - 验收：`lsof -nP -iTCP:11111 -sTCP:LISTEN` 看到 OpenD 进程在监听

- [ ] **A3. 安装 Python SDK `moomoo-api`**
  - 用户看到：终端输出 SDK 装好的版本号（≥ 10.4.6408），同时把常用依赖（pandas/numpy/matplotlib/backtrader）装齐
  - 我做：`pip3 install --upgrade moomoo-api`，并把当前 Python 版本（系统 3.9.6 偏老）与是否需要 venv 提前说明
  - 验收：`python3 -c "from moomoo import OpenQuoteContext; print('OK')"` 输出 OK

- [ ] **A4. 配置 SG 账号默认参数 + 写版本戳**
  - 用户看到：以后跑任何 moomoo 脚本不需要每次手动加 `--security-firm FUTUSG`
  - 我做：在项目本地（不进 git，不写全局 shell rc）写一份 `.envrc` 或 `.env` 设置 `FUTU_SECURITY_FIRM=FUTUSG`，并 `echo "0.1.1" > ~/.moomoo_skill_version`
  - 验收：env 变量在新 shell 里能读到

- [ ] **A5. 端到端连通性 verify**
  - 用户看到：一条命令输出 `OpenD connection successful! Server version: …, Quote login: True, Trade login: True`
  - 我做：跑 install-moomoo-opend SKILL.md 里给的 verify 片段
  - 验收：上面 3 项全为 True；如 `Quote login` 为 False，提示用户去 GUI 检查行情登录

---

## Phase B — Portfolio 拉取 skill（read-only，零交易风险）

用户视角：在 Claude Code 内说一句"看我的持仓"，立刻拿到一份对齐 moomoo App 显示的标准化报告。

- [ ] **B1. 在 investment-plugin 新增 `portfolio-fetch` skill**
  - 用户看到：`investment-plugin/skills/portfolio-fetch/` 目录，含 SKILL.md 和一个 Python 入口脚本
  - skill 调本地 `moomoo-skills` 的 `get_all_portfolios.py --json`，把结果归一化（保留 App 对齐字段：`average_cost` / `unrealized_pl` / `pl_ratio_avg_cost` / `market_val`；过滤摊薄字段）
  - 验收：`/portfolio-fetch` 输出 JSON，含 ≥1 个 SG 账户的持仓列表

- [ ] **B2. 加上行情快照拼装**
  - 用户看到：除了 qty / cost，每只持仓后面跟 P/E、52w range、市值、当日涨跌幅
  - skill 把持仓 symbol 喂给 `get_snapshot.py`（一批 ≤ 400 只）
  - 验收：每行至少 8 列（symbol / name / qty / avg_cost / last / mv / unreal_pl / pl_ratio / pe / 52w_high / 52w_low）

- [ ] **B3. 多币种汇总**
  - 用户看到：组合总市值同时显示 SGD 和 USD 两种口径
  - 用 `accinfo_query(currency=SGD)` 和 `accinfo_query(currency=USD)` 拉账户级汇总，**不**做单笔 sum
  - 验收：总市值与 moomoo App 顶部数字一致（手动比对一次）

- [ ] **B4. 人类可读 markdown 输出**
  - 用户看到：除了 JSON，还有一份 markdown 表格 + 简短结构分析（按 sector / 单只 weight / 集中度 HHI）
  - 验收：markdown 能直接贴进研究笔记

---

## Phase C — Portfolio 分析联动（与现有 stock-research 衔接）

用户视角：跑一条命令，拿到组合层面的"该卖谁、该减谁、谁还没研究过"。

- [ ] **C1. 持仓 × 历史 memo 交叉**
  - 用户看到：组合里每只股票，如果之前已用 stock-research 出过 memo，自动链接到那份 memo；没出过的标红
  - 验收：表里至少能区分"已研究"vs"未研究"

- [ ] **C2. 估值健康度扫描**
  - 用户看到：每只持仓按 §20 估值纪律打一个简短 tag（fair / stretched / cheap），用 yfinance MCP 的 P/E 和现价比 fair value 算
  - 验收：tag 与最新 memo 中的 §20 fair value 一致；无 memo 的标 `no_memo`

- [ ] **C3. 组合层风险面板**
  - 用户看到：sector concentration、单股权重 top 5、跟 SPY 的 beta-weighted exposure（粗算）
  - 验收：能跑通即可，作为 Phase 2 portfolio manager 的雏形

---

## 验证标准（整体）

- [ ] OpenD 重启 / 重新登录后，所有脚本不需要改任何代码
- [ ] 多币种数据与 moomoo App 顶部数字一致
- [ ] P&L 用 `unrealized_pl` + `pl_ratio_avg_cost`，**未出现** `pl_val` / `cost_price` / `pl_ratio`
- [ ] 速率与配额（`API_LIMITS.md`）在脚本内有保护：`get_snapshot` 自动按 400 只分批，历史 K 线前先查 `get_history_kl_quota`
- [ ] 交易接口（place_order / modify_order / cancel_order）**本期不接入**，避免误操作真实资金

---

## 关键边界

- **不接入交易**：本期 read-only。`unlock_trade` 永不调用（硬约束），下单接口本期不暴露。
- **行情权限**：moomoo SG 默认 LV1 / 延时行情即可满足 portfolio 快照需求；如发现需 LV2，单独提醒用户升级。
- **多账户**：先支持 FUTUSG 主账户。如有 paper 账户，加 `--trd-env SIMULATE` 切换。
- **加密资产**：SG 账号有 FUTUSG 加密上下文，但本期 portfolio 范围限证券，加密单列。

---

## 当前进度

环境检测已跑：Python 3.9.6（系统）/ moomoo-api 未装 / OpenD 未装 / 端口 11111 未监听 / 无版本戳 → 真正 0 状态，按 A1 开始。
