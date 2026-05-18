---
name: morning-update
description: >
  Generate a 2-minute pre-market briefing combining live moomoo holdings,
  watchlist signals, news/catalysts, and price-zone actions. Read-only — does
  not place trades. Optionally pushes to an independent Telegram bot.
  Designed to be triggered by /morning slash command or a scheduled task.
allowed-tools: Bash Read Write Edit
---

# morning-update

每个交易日早晨自动产出一份 **2 分钟可读完** 的盘前备忘，回答用户最关心的三件事：

1. 持仓里有没有事？哪些进了 Buy/Trim Zone？
2. Watchlist 里谁触发了催化剂？谁进了买入区间？
3. 哪只是今天最该 act 的（Top Call）？

## When to invoke

- 用户输入 `/morning`、"morning update"、"盘前简报"、"开盘前检查"
- Scheduled task `morning-update` fire（cron `0 8 * * 1-5` SGT，每个工作日 8:00 AM）
- 下游 skill 需要一份"持仓 + watchlist + 信号"的拼装结果

## Arguments

| 参数 | 含义 | 默认 |
|------|------|------|
| `--dry-run` | 本地生成 markdown，**不推送** Telegram | off |
| `--push` | 推送到独立 Telegram bot | off（dry-run 默认） |
| `focus:<TICKER>` | 对某只做更深的 thesis 比对（多新闻源） | none |

无参数时等价 `--dry-run`。

## Prerequisites

1. **moomoo OpenD GUI** 运行中且行情/交易双登录绿（参考 `investment-plugin/skills/portfolio-fetch/SKILL.md`）。OpenD 没启动也能跑，但报告会标"持仓数据不可用"。
2. **独立 Telegram bot**（推送时需要）：用户已通过 BotFather 创建独立 bot，并在 `~/.claude/channels/morning-update/.env` 配置 `MORNING_BOT_TOKEN` + `MORNING_CHAT_ID`（用 `grab_chat_id.py` 自动写）。
3. **Python SDK** `moomoo-api>=10.5.6508`（portfolio-fetch 已依赖）。

## Execution flow

按 6 个 step 顺序执行。**禁止跳步**或并行。

### Step 1 — 拉持仓

```bash
python3 investment-plugin/skills/portfolio-fetch/scripts/fetch_portfolio.py --json > /tmp/portfolio.json 2>/tmp/portfolio.err
```

- 成功（exit 0）→ 解析 JSON，取 `positions[]` + `funds` + `summary` + `weights`
- 失败（OpenD 没启动等）→ 标记 `portfolio_unavailable = true`，**继续后续 step**（Part 1 + Part 3 仍可跑，但 Part 2 跳过并在报告头写错误）
- positions[].code 去前缀（`US.NVDA` → `NVDA`）后用于合并 universe

### Step 2 — 读 watchlist + 合并 universe

读 `investment-plugin/references/watchlist.json`（schema 见 `references/watchlist-schema.md`）。

- 文件不存在 → 视为空 watchlist
- JSON 损坏 → **abort + 推送一条 error 消息 + exit 1**（避免静默丢数据）
- 合并：`universe = {positions[].code (stripped)} ∪ {watchlist[].ticker}`，每个 ticker 打 flag：
  - `holding` — 只在 positions
  - `watching` — 只在 watchlist
  - `both` — 两边都有

如果指定 `focus:<TICKER>`，universe 限定到该 ticker（其它静默跳过）。

### Step 3 — 加载 memo + 抽取信号

```bash
python3 investment-plugin/skills/morning-update/scripts/memo_loader.py \
  --tickers NVDA,GOOGL,MU,AMZN \
  --max-catalyst-days 30 \
  --json > /tmp/memos.json
```

每个 ticker 返回：
- `buy_zone: [low, high]` / `trim_zone: [low, high]` / `fair_value_mid` — 来自 memo §20
- `pillars: [first_pillar_sentence]` — 来自 memo §1 论点框架
- `catalysts: [{date, event, importance}]` — 来自 memo §21d（≤30 天且日期升序前 1-2 条）
- `memo_path` / `memo_date`
- `_status: "no_memo"` if 没找到

### Step 4 — 拉新闻 / 评级 / 8-K（MCP，每个 ticker 并行）

对 universe 里每个 ticker，并行调（用一条 message 里多个 tool call）：

| Tool | 用途 | 过滤 |
|------|------|------|
| `mcp__yfinance__get_news` | 隔夜新闻 | ≤24h；保留前 3 条 |
| `mcp__yfinance__get_recommendations` | 评级变动 | 近 7 天 |
| `mcp__sec-edgar__get_recent_filings` | 8-K | form_type=`"8-K"`, days=2 |
| `mcp__yfinance__get_current_stock_price` | **watching 类**当前价 | — |

`holding` 的当前价来自 portfolio-fetch snapshot（不重复拉）。

每条新闻做一次"我们的观点"判断：基于该 ticker memo §1 的 pillars，标 `confirm` / `challenge` / `noise`，**noise 丢弃**。

### Step 5 — 信号判断 + 渲染

把前面的 dict 拼成一个完整 input JSON，stdin 给渲染脚本：

```bash
cat /tmp/morning_input.json | python3 investment-plugin/skills/morning-update/scripts/render_report.py > /tmp/morning_report.md
```

input JSON 结构（详见 `references/watchlist-schema.md` 末尾 "render input schema"）：

```json
{
  "date": "2026-05-19",
  "fetched_at": "2026-05-19T08:00:00+08:00",
  "portfolio_unavailable": false,
  "funds": {...},            // 直接 forward from portfolio-fetch
  "summary": {...},
  "positions": [             // each: code, stock_name, qty, average_cost, nominal_price,
    {                        //       market_val, unrealized_pl, pl_ratio_avg_cost, today_pl_val,
      "ticker": "NVDA",      //       snapshot{...}
      ...
    }
  ],
  "watchlist": [             // each: ticker, market, name, notes, current_price
    {...}
  ],
  "memos": {                 // ticker -> memo_loader output
    "NVDA": {...}
  },
  "news": {                  // ticker -> [{title, url, opinion: confirm|challenge}]
    "NVDA": [...]
  },
  "ratings": {               // ticker -> recent changes
    "NVDA": "Buy → Strong Buy (Morgan Stanley, 2 days ago)"
  },
  "filings": {               // ticker -> recent 8-K
    "NVDA": [{date, summary, url}]
  },
  "focus": null              // or "NVDA"
}
```

渲染脚本输出 markdown 含 Top Call + Part 1/2/3。详见 §"Output format" 节。

### Step 6 — 落档 + 可选推送

1. **落档本地**（无论 dry-run / push 都做）：
   ```bash
   mkdir -p Research/_morning
   cp /tmp/morning_report.md Research/_morning/$(date +%Y-%m-%d)_morning.md
   ```

2. **推送 Telegram**（仅 `--push`）：
   ```bash
   cat /tmp/morning_report.md | python3 investment-plugin/skills/morning-update/scripts/push_telegram.py
   ```
   - Part 1 / Part 2 / Part 3 各一条消息，段间 sleep 0.5s
   - Top Call 放在 Part 1 消息开头（粗体）
   - 单段 >3900 字符 → 按 ticker 再切（≤4 条）
   - 失败重试 1 次；仍失败 → stderr + `~/.claude/channels/morning-update/_push.log` + exit 1（**本地 md 已落档不受影响**）

3. **写运行 log**：append 一行到 `Research/_morning/_run.log`，含 `{date, mode, duration_sec, positions_count, watchlist_count, exit_code}`

## Output format（rendered markdown）

```markdown
# {date} Morning Update

## 🎯 Top Call
{一句话最重要事项，例如 "MU 进入 Trim Zone，建议减仓 25-50%"}

---

## Part 1 — 今日关注

### Portfolio ({n} 只)
- **NVDA** · 持仓 · ⚡ 进入 Buy Zone
  - 催化剂：2026-05-23 GTC Asia keynote — Blackwell Ultra 出货指引
  - 重点支柱：If Blackwell capex ≥ $200B/年, then DC revenue +35% YoY through FY27
  - 隔夜：[Bloomberg 标题](url) — confirm pillar 1（DC capex 加速）
  - 评级：Buy → Strong Buy (Morgan Stanley, 2d)
- **GOOGL** · 持仓 · ✅ 正常
  - 催化剂：无 30 日内催化剂
  - ...

### Watchlist ({n} 只)
- **AMZN** · 关注 · 距 Buy Zone -7%
  - ...

---

## Part 2 — 持仓盈亏与 Action

NVDA   400 @ $192.16 → $222.43   ⚡  累计 +$12,118 (+15.8%)  今日 -$1,157  In Buy Zone → 建议加仓 1-2%
GOOGL  480 @ $268.45 → $397.20   ✅  累计 +$61,800 (+47.9%)  今日 +$273    Normal → 持有
MU      20 @ $391.00 → $679.00   ⚠️  累计 +$5,760  (+73.7%)  今日 -$913    In Trim Zone → 建议减仓 25-50%
...

**账户**：总资产 HK$4.13M / 流动性 37.6% / Top 5 集中度 61.5%（按总资产）
**风险等级**：LEVEL3

---

## Part 3 — Watchlist 入场扫描

- **AMZN** $210 — Buy Zone $180-$195 — 距 -7% — 接近 Buy Zone，待观察
- _其它静默：距离 Buy Zone > 5%，不展示_

---

_生成于 {iso8601} · 耗时 {sec}s · 持仓 {n} / 关注 {m}_
```

**纪律**：
- P&L 字段**只用** `unrealized_pl` + `pl_ratio_avg_cost`（avg cost 口径）；**禁用** `pl_val` / `pl_ratio` / `cost_price` / `diluted_cost`
- 持仓表退化为对齐纯文本（不发 markdown 表格 — Telegram 手机端不可读）
- emoji 状态：⚡ Buy Zone / ⚠️ Trim Zone / 🚫 Above Trim / ✅ Normal / ❌ Error / 📌 No memo

## Error handling

| 场景 | 行为 |
|------|------|
| OpenD 未启动（portfolio-fetch 失败） | `portfolio_unavailable=true`，Part 2 跳过，报告头标 "❌ 持仓数据不可用 — OpenD 未启动"，Part 1+3 仍跑 |
| memo 解析锚点未匹配 | 该 ticker fallback "无 zone 数据" + `_run.log` 写 parser warning |
| 当前价拿不到 | 用 portfolio-fetch 的 `prev_close_price`，标 "*盘前/休市数据" |
| watchlist.json 不存在 | 视为空，Part 3 显示 "watchlist 为空，请编辑 `investment-plugin/references/watchlist.json`" |
| watchlist.json JSON 损坏 | **abort + 推一条 error + exit 1**（不静默） |
| yfinance / sec-edgar MCP 不可用 | 该字段标 "数据源不可用"，其余照常 |
| Telegram 推送失败 | 本地 md 已落档；`_push.log` 写错误（不含 token）；exit 1 |
| 周末 | cron `1-5` 已排除；手动跑无限制 |

## Top Call 选举规则（优先级）

1. 进入 Trim Zone（动作最迫切）
2. 进入 Buy Zone（建仓机会）
3. 30 天内重大催化剂（财报 / 重要会议 / FDA / 8-K material）
4. 隔夜新闻冲击 thesis（challenge 类）
5. 都没有 → "隔夜无重大变化，维持现有仓位"

## Discipline (HARD RULES)

- **Read-only**：不调 moomoo `unlock_trade` / `place_order` / `modify_order` / `cancel_order`；本 skill 只 orchestrate + 读取
- **不修改** stock-research / valuation / decision-rules / portfolio-fetch / 现有 telegram MCP
- **不缓存** memo 解析结果（M1 现读现解析；M2 才考虑缓存）
- **不缓存** portfolio（实时拉 portfolio-fetch）
- Telegram token **永不入 git / 永不入 log**

## M2 规划（不在本 skill 范围）

- **`/research` 完成后 prompt 加 watchlist**：在 stock-research SKILL.md 末尾加 post-step，检查 ticker 不在 portfolio 也不在 watchlist 时，对话里问用户 "是否加入 watchlist？(y/n) 备注："，y 则 append 到 watchlist.json
- `/watchlist` 命令查看 / 删除 ticker
- memo 解析缓存（`cache/{ticker}.json`，mtime 失效）
- Telegram 富文本（matplotlib 渲染 P/L 柱状图）
- 财报 Quick Take 嵌入 morning note（参考 `doc/pre-market-notes-design.md` §6.3）

## Related files

- 入口：`investment-plugin/commands/morning.md`
- Scripts：
  - `scripts/memo_loader.py` — 解析 memo §1 / §20 / §21d
  - `scripts/render_report.py` — JSON → markdown
  - `scripts/push_telegram.py` — 独立 bot HTTPS POST
  - `scripts/grab_chat_id.py` — 一次性配 chat_id
- 数据：
  - `investment-plugin/references/watchlist.json`（本地维护，不入 git）
  - `~/.claude/channels/morning-update/.env`（token / chat_id）
- Cron：`~/.claude/scheduled-tasks/morning-update/SKILL.md`
- 设计稿：`doc/pre-market-notes-design.md`（v0.2，本 skill 对其做了 4 处冲突收紧，详见对应 PR 的 description）
