#!/usr/bin/env python3
"""watchlist_io — CRUD for investment-plugin/references/watchlist.json.

Schema is v1 as defined in
`investment-plugin/skills/morning-update/references/watchlist-schema.md`:

  {
    "version": 1,
    "last_updated": "YYYY-MM-DD",
    "watchlist": [
      {
        "ticker": "CORZ",
        "market": "US",
        "name": "Core Scientific",
        "notes": "AI/crypto power story; revisit after Q2 results",
        "added_at": "YYYY-MM-DD",

        // Optional extension fields (ignored by morning-update; used by
        // stock-research / future portfolio-analysis):
        "memo_path": "Research/CORZ/2026-05-19_memo.md",
        "memo_date": "2026-05-19",
        "reason": "research_completed_no_position"
      }
    ]
  }

The file is .gitignored — it is user-private local state.

Commands:
  list                          # pretty-print
  list --json                   # raw JSON
  add TICKER [--name N] [--market M] [--notes ...] [--memo-path P] [--memo-date D] [--reason R]
  remove TICKER
  check TICKER                  # exit 0 if in watchlist, 1 if not
  has-memo TICKER               # exit 0 if Research/TICKER/*memo*.md exists
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

SCHEMA_VERSION = 1


def _repo_root() -> Path:
    env = os.environ.get("INVESTMENT_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "Research").is_dir() and (parent / "investment-plugin").is_dir():
            return parent
    return Path.cwd().resolve()


def _watchlist_path() -> Path:
    return _repo_root() / "investment-plugin" / "references" / "watchlist.json"


def _empty() -> dict:
    return {
        "version": SCHEMA_VERSION,
        "last_updated": date.today().isoformat(),
        "watchlist": [],
    }


def _load() -> dict:
    p = _watchlist_path()
    if not p.exists():
        return _empty()
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("version", SCHEMA_VERSION)
    data.setdefault("watchlist", [])
    return data


def _save(data: dict) -> None:
    p = _watchlist_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data["version"] = SCHEMA_VERSION
    data["last_updated"] = date.today().isoformat()
    data["watchlist"].sort(key=lambda x: x.get("ticker", ""))
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _find_latest_memo(ticker: str) -> tuple[str, str] | None:
    research_dir = _repo_root() / "Research" / ticker
    if not research_dir.is_dir():
        return None
    memos = sorted(research_dir.glob("*memo*.md"))
    if not memos:
        return None
    latest = memos[-1]
    rel = latest.relative_to(_repo_root()).as_posix()
    head = latest.stem.split("_")[0]
    memo_date = head if (len(head) == 10 and head[4] == "-" and head[7] == "-") else ""
    return rel, memo_date


def cmd_list(args) -> int:
    data = _load()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    items = data.get("watchlist", [])
    print(f"# Watchlist v{data.get('version',1)}  (updated {data.get('last_updated','')})  — {len(items)} items")
    print(f"  file: {_watchlist_path()}\n")
    if not items:
        print("  (empty)")
        return 0
    print(f"{'Ticker':<8} {'Mkt':<4} {'Added':<12} {'Memo':<12} {'Name':<28} Notes")
    print("-" * 100)
    for it in items:
        print(
            f"{it.get('ticker',''):<8} "
            f"{it.get('market',''):<4} "
            f"{it.get('added_at',''):<12} "
            f"{it.get('memo_date',''):<12} "
            f"{(it.get('name','') or '')[:28]:<28} "
            f"{it.get('notes','')}"
        )
    return 0


def cmd_add(args) -> int:
    ticker = args.ticker.upper().strip()
    data = _load()
    if any(it.get("ticker") == ticker for it in data["watchlist"]):
        print(f"[watchlist] {ticker} already present — no change", file=sys.stderr)
        return 0

    memo_path = args.memo_path or ""
    memo_date = args.memo_date or ""
    if not memo_path or not memo_date:
        found = _find_latest_memo(ticker)
        if found:
            memo_path = memo_path or found[0]
            memo_date = memo_date or found[1]

    entry = {
        "ticker": ticker,
        "market": args.market,
        "name": args.name or ticker,
        "notes": args.notes,
        "added_at": date.today().isoformat(),
    }
    if memo_path:
        entry["memo_path"] = memo_path
    if memo_date:
        entry["memo_date"] = memo_date
    if args.reason:
        entry["reason"] = args.reason

    data["watchlist"].append(entry)
    _save(data)
    print(f"[watchlist] added {ticker}  memo={memo_path or '(none)'}", file=sys.stderr)
    return 0


def cmd_remove(args) -> int:
    ticker = args.ticker.upper().strip()
    data = _load()
    before = len(data["watchlist"])
    data["watchlist"] = [it for it in data["watchlist"] if it.get("ticker") != ticker]
    if len(data["watchlist"]) == before:
        print(f"[watchlist] {ticker} not in watchlist — no change", file=sys.stderr)
        return 1
    _save(data)
    print(f"[watchlist] removed {ticker}", file=sys.stderr)
    return 0


def cmd_check(args) -> int:
    ticker = args.ticker.upper().strip()
    data = _load()
    present = any(it.get("ticker") == ticker for it in data["watchlist"])
    if args.verbose:
        print("yes" if present else "no")
    return 0 if present else 1


def cmd_has_memo(args) -> int:
    ticker = args.ticker.upper().strip()
    found = _find_latest_memo(ticker)
    if args.verbose:
        print(found[0] if found else "(none)")
    return 0 if found else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="watchlist CRUD (v1 schema)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("add")
    sp.add_argument("ticker")
    sp.add_argument("--name", default="", help="display name; default = ticker")
    sp.add_argument("--market", default="US")
    sp.add_argument("--notes", default="", help="one-line trigger / context")
    sp.add_argument("--memo-path", default="")
    sp.add_argument("--memo-date", default="")
    sp.add_argument("--reason", default="research_completed_no_position")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("remove")
    sp.add_argument("ticker")
    sp.set_defaults(func=cmd_remove)

    sp = sub.add_parser("check")
    sp.add_argument("ticker")
    sp.add_argument("--verbose", "-v", action="store_true")
    sp.set_defaults(func=cmd_check)

    sp = sub.add_parser("has-memo")
    sp.add_argument("ticker")
    sp.add_argument("--verbose", "-v", action="store_true")
    sp.set_defaults(func=cmd_has_memo)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
