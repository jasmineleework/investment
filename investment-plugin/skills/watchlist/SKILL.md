---
name: watchlist
description: >
  Manage the research watchlist — tickers with a completed memo but no live
  position. Use after `stock-research` finishes, when the user asks "看 watchlist",
  "我的关注列表", "加入观察池", "remove from watchlist", or whenever you need to
  decide if a freshly-researched ticker should be tracked going forward. Reads /
  writes `investment-plugin/references/watchlist.json` (v1 schema, shared with
  `morning-update`).
allowed-tools: Bash Read
---

# watchlist

Single source of truth: **`investment-plugin/references/watchlist.json`** (the
exact path `morning-update` already reads — see
`skills/morning-update/references/watchlist-schema.md`). The file is in
`.gitignore` — local & private.

Each entry records a ticker that has a completed research memo but is **not**
in the live portfolio. Downstream skills (`morning-update`, future
`portfolio-analysis`) iterate over it to know which non-held names still
deserve attention.

## Schema (v1 — must match morning-update)

```json
{
  "version": 1,
  "last_updated": "YYYY-MM-DD",
  "watchlist": [
    {
      "ticker": "CORZ",
      "market": "US",
      "name": "Core Scientific",
      "notes": "AI/crypto power story; revisit after Q2",
      "added_at": "YYYY-MM-DD",

      "memo_path": "Research/CORZ/2026-05-19_memo.md",
      "memo_date": "2026-05-19",
      "reason": "research_completed_no_position"
    }
  ]
}
```

`ticker`, `market`, `name`, `notes`, `added_at` are read by `morning-update`.
`memo_path`, `memo_date`, `reason` are local extension fields used by
`stock-research` Step 11 and future `portfolio-analysis`; `morning-update`
ignores unknown keys.

`watchlist[]` is sorted by ticker after every mutation; the file is rewritten
by the script — never hand-edit unless you also bump `last_updated`.

## CLI

```bash
SCRIPT=investment-plugin/skills/watchlist/scripts/watchlist_io.py

# show
python3 $SCRIPT list
python3 $SCRIPT list --json

# add (auto-discovers latest memo under Research/{TICKER}/)
python3 $SCRIPT add CORZ --name "Core Scientific" --market US
python3 $SCRIPT add CORZ --name "Core Scientific" --notes "watch Q2 earnings call"

# remove (e.g. when the user buys it and it becomes a real holding)
python3 $SCRIPT remove CORZ

# scripted checks — exit 0 = yes, 1 = no
python3 $SCRIPT check CORZ           # is in watchlist?
python3 $SCRIPT has-memo CORZ        # has a memo on disk?
```

The script auto-locates the repo root by walking up from itself until it finds
a parent that contains both `Research/` and `investment-plugin/`. Override
with `INVESTMENT_ROOT=/abs/path` when running from an unusual cwd.

## When to invoke

1. **End of a research run** — `stock-research` Step 11:
   - call `check {ticker}` and inspect live `positions[]`;
   - if neither held nor watchlisted, ask the user inline; on confirmation run
     `add {ticker} --name "..." --notes "..."` and report stderr.

2. **Holding changes** — when the user buys a watchlisted ticker, run
   `remove {ticker}` so morning-update treats it as a position instead. When
   the user sells a position but explicitly wants to keep tracking it, run
   `add {ticker} --reason exited_keep_tracking`.

3. **User asks** — "看 watchlist" / "remove X" / "加 Y 进观察池" — run the
   matching command and surface stdout/stderr.

## Hard rules

- **Idempotent add**: re-adding an existing ticker is a no-op (stderr note,
  exit 0). Never duplicate rows.
- **Uppercase, no prefix**: the script normalises to upper-case automatically;
  never store `us.corz`, `$CORZ`, etc.
- **Non-held only**: do not add a ticker the user currently holds. Watchlist
  is for tickers *outside* the portfolio.
- **Memo first**: only auto-fill `memo_path`/`memo_date` from disk. If a user
  asks to add a no-memo ticker, suggest running `/research {ticker}` first;
  if they insist, leave those fields empty and put the rationale in `--notes`.
- **Stay schema-stable**: this file is `morning-update`'s input contract. Do
  not rename top-level keys (`version` / `last_updated` / `watchlist`) or the
  required item fields (`ticker` / `market` / `name` / `notes` / `added_at`).
  Adding new optional fields is safe — `morning-update` ignores unknown keys.

## Downstream consumers

- `morning-update` Part 3 — iterates `watchlist[]` and pulls a price/news
  snapshot for each, surfacing Buy-Zone entries and pending catalysts.
- Future `portfolio-analysis` — diff portfolio ↔ watchlist ↔ research corpus
  to surface "researched but never acted on" decisions.
