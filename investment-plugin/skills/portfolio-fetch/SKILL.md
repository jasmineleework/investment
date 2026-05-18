---
name: portfolio-fetch
description: >
  Pull real-time positions, account funds, and quote snapshots from moomoo OpenAPI
  for portfolio analysis. Read-only — no trading. Defaults to FUTUSG (moomoo SG)
  real account; auto-detects acc_id. Outputs markdown report (default) or JSON.
  Field mapping aligns with moomoo App display (uses unrealized_pl /
  pl_ratio_avg_cost; never cost_price / pl_val / pl_ratio).
allowed-tools: Bash Read
---

# portfolio-fetch

Pull the user's live moomoo SG portfolio (positions + funds + per-symbol quote snapshot) and render it as a markdown report or JSON. Designed to feed downstream portfolio analysis skills.

## When to invoke

- User asks "show my positions", "看我的持仓", "我的组合", "current portfolio", "投资组合现状"
- User asks for account summary, total assets, cash balance, P&L
- Downstream skill needs a normalized portfolio JSON (e.g. concentration analysis, valuation cross-check)

## Prerequisites

1. moomoo OpenD GUI is running and **logged in** (Quote login + Trade login both green). If not, ask user to launch `/Applications/moomoo_OpenD.app` and log in. Do **not** prompt for or accept account credentials yourself.
2. Python SDK `moomoo-api>=10.5.6508` installed in user site (already present via earlier setup).
3. **Do not** ask the user to click "Unlock Trade" in OpenD — this skill is read-only and does not place orders.

## Usage

```bash
# default: markdown report to stdout
python3 investment-plugin/skills/portfolio-fetch/scripts/fetch_portfolio.py

# raw JSON (for downstream skills)
python3 investment-plugin/skills/portfolio-fetch/scripts/fetch_portfolio.py --json

# both formats
python3 investment-plugin/skills/portfolio-fetch/scripts/fetch_portfolio.py --both

# override account (rare; default is auto-detected SG real account)
python3 investment-plugin/skills/portfolio-fetch/scripts/fetch_portfolio.py --acc-id <YOUR_ACC_ID>
```

Environment overrides (optional):
- `MOOMOO_PORTFOLIO_ACC_ID` — pin a specific account id (skips auto-detect)
- `FUTU_OPEND_HOST` / `FUTU_OPEND_PORT` — non-default OpenD address

## Output shape (JSON)

```json
{
  "acc_id": <int>,
  "security_firm": "FUTUSG",
  "fetched_at": "<ISO8601>",
  "funds": {
    "hkd": { "total_assets": ..., "market_val": ..., "cash": ..., "available_funds": ..., "power": ..., "risk_status": "LEVEL3" },
    "usd": { ... same shape ... }
  },
  "positions": [
    {
      "code": "US.NVDA",
      "stock_name": "NVIDIA",
      "position_market": "US",
      "currency": "USD",
      "qty": 400.4,
      "can_sell_qty": 400.4,
      "average_cost": 192.164,
      "nominal_price": 222.43,
      "market_val": 89060.97,
      "unrealized_pl": 12118.635,
      "pl_ratio_avg_cost": 15.75,
      "realized_pl": 8.02,
      "today_pl_val": -1157.156,
      "snapshot": {
        "last_price": 222.43,
        "pe_ratio": 45.371,
        "pb_ratio": 34.234,
        "pe_ttm_ratio": ...,
        "earning_per_share": ...,
        "highest52weeks_price": ...,
        "lowest52weeks_price": ...,
        "total_market_val": 5384707168022.0,
        "dividend_ratio_ttm": ...
      }
    }
  ],
  "summary": {
    "total_market_val_usd": ...,
    "n_positions": 11,
    "top5_concentration_pct": ...,
    "hhi": ...
  }
}
```

## Field discipline (hard rules)

Aligned with `moomoo-skills/skills/moomooapi/docs/FIELD_MAPPING.md`:

- **P&L**: use `unrealized_pl` + `pl_ratio_avg_cost` (avg cost basis). Never use `pl_val` / `pl_ratio` / `cost_price` / `diluted_cost` — those use diluted cost and disagree with the moomoo App display.
- **Account-level aggregation**: use `accinfo_query(currency=...)` for total market value per currency. Never sum `positions[].market_val` across mixed currencies.
- **Multi-currency**: this skill fetches both HKD-base and USD-base account views and returns both.

## Limits

- Snapshot batch size: 400 codes per `get_market_snapshot` call (auto-batched inside the script).
- No subscription quota consumed (snapshot uses session-cached or delayed quote).
- No trading interface exposed. `unlock_trade` is never called.

## Failure modes

| Symptom | Cause | Resolution |
|---|---|---|
| `Cannot connect to OpenD (127.0.0.1:11111)` | OpenD GUI not running or not logged in | Ask user to launch and log in |
| `No REAL non-MASTER account found` | OpenD logged into wrong account / no live SG account | Verify SG login in OpenD GUI |
| Snapshot returns empty for some codes | Quote permission gap (e.g. JP, or non-LV1 markets) | Note in report; position data still valid |
| Pre/post market or weekend | `nominal_price` may equal `prev_close_price` | Report normal — moomoo App shows the same |

## Downstream consumers

- `portfolio-analysis` (Phase C) — concentration, sector/market exposure, beta-weighted risk
- `stock-research` — cross-reference each holding against existing memos
- Manual: paste markdown into investment journal
