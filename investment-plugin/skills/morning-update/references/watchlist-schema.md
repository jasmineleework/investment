# Watchlist Schema & Maintenance

`investment-plugin/references/watchlist.json` stores **manually-curated** tickers you want to monitor but don't necessarily hold. Used by the `morning-update` skill.

> **Important**: this file is in `.gitignore` — your watchlist is local & private.

## Schema (v1)

```json
{
  "version": 1,
  "last_updated": "2026-05-19",
  "watchlist": [
    {
      "ticker": "AMZN",
      "market": "US",
      "name": "Amazon.com",
      "notes": "等 AWS 增速回到 20%+ 后再进",
      "added_at": "2026-04-12"
    }
  ]
}
```

### Fields

| Field | Required | Type | Notes |
|---|---|---|---|
| `version` | yes | int | Schema version; bump if breaking changes |
| `last_updated` | yes | str | YYYY-MM-DD; update when you edit |
| `watchlist[].ticker` | yes | str | **No market prefix** (e.g. `"AMZN"`, not `"US.AMZN"`). morning-update strips `US.`/`HK.` from portfolio codes to match |
| `watchlist[].market` | yes | str | `"US"` / `"HK"` / `"SH"` / `"SZ"` / `"SG"` |
| `watchlist[].name` | yes | str | Display name (free-form) |
| `watchlist[].notes` | no | str | One-line trigger description (only for your reference) |
| `watchlist[].added_at` | no | str | YYYY-MM-DD |

## What's NOT in this file

By design — morning-update reads these **fresh every run**, not cached:

- ❌ `buy_zone` / `trim_zone` / `fair_value_mid` → read from the latest `Research/{ticker}/*_memo.md` §20
- ❌ `pillars` / `catalysts` → read from memo §1 / §21d
- ❌ `current_price` → live via yfinance MCP (watchlist) or portfolio-fetch snapshot (holdings)
- ❌ `rating` → live via decision-rules / yfinance recommendations

This keeps the file extremely stable. If you update a memo's Buy Zone today, tomorrow's morning update reflects it automatically — no separate sync step.

## Maintenance workflow (M1 — manual)

```bash
# View
cat investment-plugin/references/watchlist.json | python3 -m json.tool

# Edit
$EDITOR investment-plugin/references/watchlist.json
```

After editing, bump `last_updated`. The morning-update skill reads the file each run — no restart needed.

### Add a ticker

1. Open the file
2. Add a new object to `watchlist[]` with at minimum `ticker`, `market`, `name`
3. If you haven't researched it yet, run `/research {ticker}` first — morning-update will show "📌 未做研究" for tickers without a memo, but Buy Zone signals require a memo

### Remove a ticker

1. Delete its object from `watchlist[]`

## M2 planning (not yet implemented)

- **Auto-prompt on `/research` completion**: after a memo is generated, stock-research will check if the ticker is in `positions` or `watchlist`. If neither, prompt "Add to watchlist? (y/n) Notes:". Confirmed → append.
- `/watchlist` command for inline view/edit
- Memo parse caching (`cache/{ticker}.json`, mtime invalidation)

## Memo parser anchors (memo_loader.py)

For reference — these are the regex anchors memo_loader.py uses against `Research/{ticker}/*_memo.md`:

| Section | Anchor regex (Python) |
|---|---|
| §1 Thesis | `^#{1,3}\s*(?:§\s*)?1\.?\s*(?:论点框架\|Thesis Framework\|Thesis)` |
| §20 Valuation | `^#{1,3}\s*(?:§\s*)?20\.?\s*(?:估值框架\|Valuation Framework\|Valuation)` |
| §21 Scenarios | `^#{1,3}\s*(?:§\s*)?21\.?\s*(?:场景分析\|Scenarios\|Scenario)` |
| Pillar title | `\*\*(?:Thesis\s*)?(?:Pillar\|支柱)\s*\d+\s*[:：]\s*([^\n*]+?)\*\*` |
| Buy Zone row | `\|\s*Buy Zone\s*\|\s*\$([\d,.]+)[\s]*[–—-][\s]*\$([\d,.]+)` |
| Trim Zone row | `\|\s*Trim Zone\s*\|\s*\$([\d,.]+)[\s]*[–—-][\s]*\$([\d,.]+)` |
| Fair Value Range | `\|\s*\*?\*?Fair Value Range\*?\*?\s*\|\s*\$X[\s]*[–—-][\s]*\$X[\s]*[–—-][\s]*\$X` (low–mid–high) |
| Catalyst row | `^\|\s*(\d{4}-\d{2}-\d{2})(?:\s*\([^)]*\))?\s*\|\s*([^|]+?)\s*\|` |

If you change memo template formatting, update these anchors and re-run on a known memo (e.g. `Research/MU/2026-05-10_memo.md`) to verify the parser still works.
