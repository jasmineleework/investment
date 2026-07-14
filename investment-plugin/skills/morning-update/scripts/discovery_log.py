#!/usr/bin/env python3
"""
discovery_log.py — append-only history of morning-update Discovery picks.

Log file: Research/_morning/discovery_log.json — a JSON array of:
  {date, type: "concept"|"ticker", name, tickers: [..], one_liner,
   source_articles: [{title, url}]}

Subcommands:
  list --days 30        recent entries (JSON to stdout) — feed to the
                        exclusion set before picking today's idea
  add --json '<entry>'  append one entry (validates shape, rewrites file
                        atomically so a crash can't corrupt the log)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
LOG_PATH = REPO_ROOT / "Research" / "_morning" / "discovery_log.json"

REQUIRED_FIELDS = {"date", "type", "name", "one_liner", "source_articles"}


def load_log() -> list:
    if not LOG_PATH.exists():
        return []
    try:
        data = json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"FATAL: corrupt {LOG_PATH}: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, list):
        print(f"FATAL: {LOG_PATH} is not a JSON array", file=sys.stderr)
        sys.exit(1)
    return data


def cmd_list(days: int) -> int:
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    recent = [e for e in load_log() if e.get("date", "") >= cutoff]
    json.dump(recent, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_add(raw: str) -> int:
    try:
        entry = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"FATAL: --json is not valid JSON: {e}", file=sys.stderr)
        return 1
    missing = REQUIRED_FIELDS - set(entry)
    if missing:
        print(f"FATAL: entry missing fields: {sorted(missing)}", file=sys.stderr)
        return 1
    if entry["type"] not in ("concept", "ticker"):
        print("FATAL: type must be 'concept' or 'ticker'", file=sys.stderr)
        return 1
    arts = entry["source_articles"]
    if not isinstance(arts, list) or not arts or not all(a.get("url") for a in arts):
        print("FATAL: source_articles must be a non-empty list of {title, url}", file=sys.stderr)
        return 1
    entry.setdefault("tickers", [])

    log = load_log()
    log.append(entry)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(LOG_PATH.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, LOG_PATH)
    print(f"added: {entry['name']} ({entry['date']})", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Discovery pick history")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list")
    p_list.add_argument("--days", type=int, default=30)
    p_add = sub.add_parser("add")
    p_add.add_argument("--json", required=True, help="entry as JSON string")
    args = ap.parse_args()
    if args.cmd == "list":
        return cmd_list(args.days)
    return cmd_add(args.json)


if __name__ == "__main__":
    sys.exit(main())
