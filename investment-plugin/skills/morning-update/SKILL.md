---
name: morning-update
description: >
  Generate a 10-minute morning briefing: curated news + opinions for watchlist
  tickers and concepts (RSS aggregation incl. must-push sources like Citrini
  Research), one daily discovery idea with source article, and conditional
  buy/trim trade signals. Read-only — does not place trades. Optionally pushes
  to an independent Telegram bot. Triggered by /morning or a scheduled task.
allowed-tools: Bash Read Write Edit WebFetch WebSearch
---

# morning-update

每个交易日产出一份 **10 分钟可读完** 的晨间简报，回答四件事：

1. 今天有哪些**必读文章**？（Citrini Research 等 must-push 源有新文一定推）
2. watchlist 标的和背后概念（TPU 供应链、AI infra …）今天有什么**重点新闻 + 我们的观点**？
3. 市场上有没有一个**我还没发现**的概念/标的值得研究？（每天 1 个，必须附文章）
4. 有没有**交易信号**？（watchlist 进 Buy Zone / 持仓进 Trim Zone —— 有才出现）

## When to invoke

- 用户输入 `/morning`、"morning update"、"晨报"、"盘前简报"
- Scheduled task fire（每天北京时间 08:00 复盘视角 + 21:30 美股开盘视角）
- 下游 skill 需要一份"新闻 + 信号"拼装结果

## Arguments

| 参数 | 含义 | 默认 |
|------|------|------|
| `--dry-run` | 本地生成 markdown，**不推送** Telegram | off |
| `--push` | 推送到独立 Telegram bot | off（dry-run 默认） |
| `focus:<TICKER>` | 只对某只做深挖 | none |

无参数时等价 `--dry-run`。

## Prerequisites

1. **moomoo OpenD GUI**（可选）：没启动也能跑，交易信号只覆盖 watchlist，报告头标注。
2. **独立 Telegram bot**（推送时需要）：`~/.claude/channels/morning-update/.env` 配置 `MORNING_BOT_TOKEN` + `MORNING_CHAT_ID`。
3. 网络可达 RSS 源（`references/feeds.json`）。

## Execution flow

按 8 个 step 顺序执行。Step 1 失败不阻塞。

### Step 1 — 拉持仓（可选，用于 trim 信号）

```bash
python3 investment-plugin/skills/portfolio-fetch/scripts/fetch_portfolio.py --json > /tmp/portfolio.json 2>/tmp/portfolio.err
```

- 成功 → 取 `positions[]`（只需要 code / nominal_price / snapshot.last_price）
- 失败 → `portfolio_unavailable = true`，**继续**（交易信号只覆盖 watchlist）

### Step 2 — 读 watchlist + concepts

- `investment-plugin/references/watchlist.json`（损坏则 abort + error，不静默）
- `investment-plugin/references/concepts.json`（概念关键词；不存在视为空）
- `universe = {positions} ∪ {watchlist}`；`focus:<TICKER>` 时限定

### Step 3 — memo 抽 zone

```bash
python3 investment-plugin/skills/morning-update/scripts/memo_loader.py \
  --tickers <universe CSV> --max-catalyst-days 30 --json > /tmp/memos.json
```

无 memo 的 watchlist 标的由渲染脚本从 notes 里 fallback 提取买入区（如 "买入区 $95–110"）。

### Step 4 — RSS 聚合

```bash
python3 investment-plugin/skills/morning-update/scripts/news_fetch.py \
  --tickers <universe CSV> --hours 24 --json > /tmp/news_candidates.json
```

输出四桶：
- `must_push` — Citrini 等 must-push 源新文章（48h 窗口、跳过关键词过滤）
- `matched` — 按 ticker / concept id 分组的命中新闻
- `macro` — 宏观关键词命中
- `unmatched_hot` — 高热度未匹配标题簇（Discovery 素材）

补充（少量 MCP）：
- 持仓 ticker：`mcp__sec-edgar__get_recent_filings`（form_type="8-K", days=2）
- 某信号 ticker 在 `matched` 里为空时：fallback `mcp__yfinance__get_news`

### Step 5 — LLM 策展（观点生成）

读 `/tmp/news_candidates.json` + memos（§1 pillars）+ watchlist notes，产出：

1. **must_read**：每篇 must_push 文章，用 WebFetch 抓正文写 3-5 句核心论点摘要 + 与 watchlist 的关联（付费墙截断时基于可见部分并注明）。**must_push 桶里的文章一篇都不能丢。**
2. **worth_reading**：从 opinion 源（Seeking Alpha 等）+ matched 桶挑 1-3 篇值得读的深度内容，每篇写"为什么值得读"。
3. **news_curated**：5-8 条重点新闻，优先级 challenge thesis > 概念级事件 > confirm；每条写 1 句事实 + 2-3 句观点（so-what），标 stance（confirm/challenge/neutral）。
4. **concept_pulse**：3-5 句概念温度计综述（TPU 供应链 / AI 电力等今天整体动向）。

去重纪律：同一事件多源报道只保留一条（选最权威源）。

### Step 6 — Discovery（每天 1 个新 idea）

1. `python3 investment-plugin/skills/morning-update/scripts/discovery_log.py list --days 30` → 近 30 天已推荐
2. 排除集 = holdings ∪ watchlist ∪ 已推荐
3. 从 `unmatched_hot` 标题簇出发，必要时 1-2 次 WebSearch 验证（如 `"<keyword> investment theme 2026"`）
4. **硬性要求：必须附至少 1 篇来源文章链接**；无可引用文章的 idea 不合格
5. 产出后写回历史：
   ```bash
   python3 .../discovery_log.py add --json '{"date":"...","type":"concept|ticker","name":"...","tickers":[...],"one_liner":"...","source_articles":[{"title":"...","url":"..."}]}'
   ```
6. 无合格 idea → `discovery = {"none_today": true, "scanned_note_cn": "扫描了哪些热点"}`（连续跳过可接受，不硬凑）

### Step 7 — 拼装 + 渲染

把 Step 1-6 结果拼成 input JSON v2（schema 见 `references/watchlist-schema.md` 末尾）。

**URL 完整性校验（必跑，防止手敲/截断的死链）**：

```bash
python3 investment-plugin/skills/morning-update/scripts/check_urls.py /tmp/morning_input.json /tmp/news_candidates.json
```

FAIL 则回到 Step 5 从 candidates JSON 原样复制 URL（禁止从终端截断显示里手抄；WSJ 等 URL 末尾带唯一 hash，截断即 404）。通过后渲染：

```bash
cat /tmp/morning_input.json | python3 investment-plugin/skills/morning-update/scripts/render_report.py > /tmp/morning_report.md
```

渲染脚本负责：Top Call 选举（信号 > must_read > 默认）、Part 1-3 常设渲染、**Part 4 只在有 buy/trim 信号时渲染**、notes zone fallback。

### Step 8 — 落档 + 可选推送

1. 落档：`cp /tmp/morning_report.md Research/_morning/$(date +%Y-%m-%d)_morning.md`
2. 推送（仅 `--push`）：`cat /tmp/morning_report.md | python3 .../push_telegram.py`
   - 切分按 `## Part 1/2/3`；Part 4 内容自然并入 Part 3 那条消息（push_telegram 不改）
3. `_run.log` append 一行：`{date, mode, duration_sec, news_scanned, news_kept, must_push_count, discovery, signals_count, exit_code}`

## Output format

```markdown
# {date} Morning Update

## 🎯 Top Call
{一句话：交易信号 > Citrini 新文 > "今日以阅读为主"}

## Part 1 — 必读文章
### 📌 Citrini Research
**[标题](url)**
- 3-5 句核心论点摘要
- 与 watchlist 的关联：…
### 值得读
- **[标题](url)** · 来源
  - 为什么值得读

## Part 2 — 新闻与观点
### 概念温度计
{3-5 句综述}
### 重点新闻（5-8 条）
- **[标题](url)** · 来源 · AVGO · ✅ confirm
  - 事实：…
  - 观点：…

## Part 3 — 今日发现
**{名称}**（概念 · 相关标的：…）
- 是什么 / 为什么有潜力 / 与 watchlist 的差异 / 来源文章 / 下一步

## Part 4 — 交易信号        ← 条件板块：无信号时整段不出现
### 🟢 Buy Zone
- **AVGO** $200.00 · Buy Zone $187.00–$215.00 · watchlist 建仓 · 建议限价 $201.00
### 🔴 Trim / Sell
- **MU** $560.00 · Trim Zone $525.00–$630.00 · 建议减仓 25-50% · 挂单参考 $525.00（zone 下沿）

_生成于 {iso8601} · 扫描 N 条 → 保留 M 条_
```

篇幅纪律：全文 2000-2500 中文字（10 分钟）；Part 1 ~30% / Part 2 ~50% / Part 3 ~20%。

## Error handling

| 场景 | 行为 |
|------|------|
| OpenD 未启动 | `portfolio_unavailable=true`，trim 信号跳过，报告头标注，其余照常 |
| 单个 RSS 源失败 | news_fetch 静默降级（stderr 记录），其余源照常 |
| Citrini WebFetch 付费墙 | 摘要基于 RSS summary + 可见部分，注明"限免/付费墙" |
| memo 解析失败 | 该 ticker fallback notes 提取；再无则无信号 |
| watchlist.json 损坏 | abort + 推 error + exit 1 |
| discovery 无合格 idea | `none_today`，不硬凑 |
| Telegram 推送失败 | 本地 md 已落档；`_push.log` 记录；exit 1 |

## Discipline (HARD RULES)

- **Read-only**：不调 moomoo 下单类接口
- **must_push 桶零丢弃**：Citrini 等源的新文章必须全部出现在 Part 1
- **Discovery 必须附文章链接**，且 30 天内不重复推荐（先 `discovery_log.py list`）
- 观点必须落到"对 thesis / 决策的含义"，禁止复述 headline
- Telegram token 永不入 git / 永不入 log
- 不缓存 RSS / memo / portfolio（每次现拉）

## Related files

- 入口：`investment-plugin/commands/morning.md`
- Scripts（skill-local）：
  - `scripts/news_fetch.py` — RSS 聚合四桶输出
  - `scripts/discovery_log.py` — Discovery 历史 list/add
  - `scripts/memo_loader.py` — 解析 memo §1 / §20 / §21d
  - `scripts/render_report.py` — input JSON v2 → markdown
  - `scripts/push_telegram.py` — 独立 bot HTTPS POST
  - `scripts/grab_chat_id.py` — 一次性配 chat_id
- 数据：
  - `references/feeds.json` — RSS 源清单（must_push 标记；用户可自行加 Substack）
  - `investment-plugin/references/concepts.json` — 概念关键词
  - `investment-plugin/references/watchlist.json`（本地维护，不入 git）
  - `Research/_morning/discovery_log.json` — Discovery 历史
  - `~/.claude/channels/morning-update/.env`（token / chat_id）
- 设计稿：`doc/pre-market-notes-design.md`、`doc/narrative-screener-design.md`（Discovery 轻量版思路来源）
