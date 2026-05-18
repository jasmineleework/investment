---
description: Pre-market morning briefing — live holdings, watchlist signals, news, price-zone actions; optional push to Telegram
argument-hint: "[--push] [--dry-run] [focus:<ticker>]"
---

# /morning

Generate a 2-minute pre-market briefing combining your moomoo SG holdings, watchlist signals, overnight news/catalysts, and price-zone-driven actions. Read-only — never places trades.

## Usage

```
/morning                # markdown report to stdout + Research/_morning/ (no push)
/morning --dry-run      # same as above (explicit no-push)
/morning --push         # push 3 messages to your independent Telegram bot
/morning focus:NVDA     # deep-dive on a single ticker
/morning focus:NVDA --push
```

## Behavior

Loads the `morning-update` skill and follows its 6-step execution flow:

1. Pull live positions via `portfolio-fetch` (read-only, requires moomoo OpenD running)
2. Read `investment-plugin/references/watchlist.json`; merge with positions into universe
3. Extract memo signals (§1 pillars / §20 Buy & Trim Zones / §21d catalysts ≤30 days) for every ticker in universe
4. Pull overnight news (yfinance), rating changes, recent 8-Ks (sec-edgar) for the same universe
5. Render Markdown report (Top Call + Part 1 关注 + Part 2 持仓盈亏 + Part 3 watchlist 入场扫描)
6. Save to `Research/_morning/{date}_morning.md`; if `--push`, send 3 messages to Telegram via `scripts/push_telegram.py`

See `skills/morning-update/SKILL.md` for the full spec.

## Prerequisites

- moomoo OpenD GUI running and logged in (Quote + Trade login both green). OpenD off → report still generates without Part 2.
- For `--push`: configured independent Telegram bot — token + chat_id in `~/.claude/channels/morning-update/.env` (run `scripts/grab_chat_id.py` for first-time setup)

## Output

- **stdout**: full markdown report
- **file**: `Research/_morning/{date}_morning.md`
- **log**: appended to `Research/_morning/_run.log`
- **Telegram** (if `--push`): 3 messages (Part 1+TopCall, Part 2, Part 3)

## Failure modes

| Scenario | Behavior |
|---|---|
| OpenD not running | Report header marks "❌ 持仓数据不可用"; Parts 1 and 3 still run |
| `watchlist.json` missing | Treated as empty watchlist; Part 3 prompts to edit |
| `watchlist.json` JSON corrupt | Abort + push error message + exit 1 |
| Telegram push fails | Local markdown still saved; `_push.log` records the error (no token leak) |
| Weekend | Manual `/morning` works; scheduled task cron `1-5` skips Sat/Sun |
