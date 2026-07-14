---
description: 10-minute morning briefing — must-read articles (Citrini etc.), curated news + opinions for watchlist tickers/concepts, one daily discovery idea, conditional buy/trim signals; optional push to Telegram
argument-hint: "[--push] [--dry-run] [focus:<ticker>]"
---

# /morning

Generate a 10-minute morning briefing: RSS-aggregated news with opinions for your watchlist tickers and their underlying concepts, must-push articles (Citrini Research), one daily discovery idea (always with a source article), and a conditional trade-signal section. Read-only — never places trades.

## Usage

```
/morning                # markdown report to stdout + Research/_morning/ (no push)
/morning --dry-run      # same as above (explicit no-push)
/morning --push         # push to your independent Telegram bot
/morning focus:NVDA     # deep-dive on a single ticker
/morning focus:NVDA --push
```

## Behavior

Loads the `morning-update` skill and follows its 8-step execution flow:

1. Pull live positions via `portfolio-fetch` (optional — only feeds trim signals)
2. Read `watchlist.json` + `concepts.json`; merge universe
3. Extract memo zones via `memo_loader.py`
4. Aggregate RSS via `news_fetch.py` (four buckets: must_push / matched / macro / unmatched_hot)
5. LLM curation: must-read summaries (WebFetch full text), 5-8 curated news items with so-what opinions, concept pulse paragraph
6. Discovery: one new concept/ticker not in watchlist and not recommended in last 30 days, with ≥1 source article (`discovery_log.py`)
7. Assemble input JSON v2 → `render_report.py`
8. Save to `Research/_morning/{date}_morning.md`; if `--push`, send via `push_telegram.py`

See `skills/morning-update/SKILL.md` for the full spec.

## Prerequisites

- For trim signals: moomoo OpenD GUI running (optional — report generates without it)
- For `--push`: token + chat_id in `~/.claude/channels/morning-update/.env` (run `scripts/grab_chat_id.py` for first-time setup)

## Output

- **stdout**: full markdown report
- **file**: `Research/_morning/{date}_morning.md`
- **log**: appended to `Research/_morning/_run.log`; discovery appended to `Research/_morning/discovery_log.json`
- **Telegram** (if `--push`): 3 messages (Part 1+TopCall, Part 2, Part 3 — trade signals ride with the last message when triggered)

## Failure modes

| Scenario | Behavior |
|---|---|
| OpenD not running | Header marks "持仓数据不可用"; signals cover watchlist only |
| Single RSS feed down | `news_fetch.py` degrades silently (stderr stats); other feeds unaffected |
| `watchlist.json` missing | Treated as empty watchlist |
| `watchlist.json` JSON corrupt | Abort + push error message + exit 1 |
| No qualified discovery idea | "今日无新发现" with scanned note — never forced |
| Telegram push fails | Local markdown still saved; `_push.log` records the error (no token leak) |
