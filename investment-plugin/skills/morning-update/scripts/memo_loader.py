#!/usr/bin/env python3
"""
memo_loader.py — extract structured signals from the latest stock-research memo.

Scans Research/{TICKER}/, finds the most recently modified `*_memo.md` (excludes
`*_quick-check.md` and `data_contract.md`), and pulls:

- §1 Thesis pillars (first sentence per pillar bullet)
- §20 Buy Zone / Trim Zone / Fair Value Mid (low–mid–high triple)
- §21d Catalysts (within --max-catalyst-days, date-ascending, top 2)

Output: JSON to stdout. Read by morning-update orchestrator.

Bilingual anchor support (CN/EN), tolerant of en-dash `–` vs hyphen `-`.

Discipline: NEVER reference pl_val / pl_ratio (non-_avg_cost) / cost_price /
diluted_cost in extracted fields — those are P&L territory, not memo territory.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]  # .../Investment/
RESEARCH_DIR = REPO_ROOT / "Research"

# ---------------------------------------------------------------------------
# Section locators (bilingual)
# ---------------------------------------------------------------------------

# §1 Thesis: matches "## §1 ..." or "## 1. ..." or "## Thesis Framework"
SEC1_RE = re.compile(r"^#{1,3}\s*(?:§\s*)?1\.?\s*(?:论点框架|Thesis Framework|Thesis)", re.IGNORECASE | re.MULTILINE)
SEC20_RE = re.compile(r"^#{1,3}\s*(?:§\s*)?20\.?\s*(?:估值框架|Valuation Framework|Valuation)", re.IGNORECASE | re.MULTILINE)
SEC21_RE = re.compile(r"^#{1,3}\s*(?:§\s*)?21\.?\s*(?:场景分析|Scenarios|Scenario)", re.IGNORECASE | re.MULTILINE)

# ---------------------------------------------------------------------------
# Cell-level regex
# ---------------------------------------------------------------------------

# Money cell e.g. "$273", "$273.5", with optional thousands sep
MONEY = r"\$\s*([\d,]+(?:\.\d+)?)"
# Dash separator that may be en-dash, em-dash, or hyphen
DASH = r"[\s]*[–—-][\s]*"

# `| Buy Zone | $273 – $315 | ... |`  →  groups: low, high
BUY_ZONE_RE = re.compile(rf"\|\s*Buy Zone\s*\|\s*{MONEY}{DASH}{MONEY}", re.IGNORECASE)
TRIM_ZONE_RE = re.compile(rf"\|\s*Trim Zone\s*\|\s*{MONEY}{DASH}{MONEY}", re.IGNORECASE)

# Fair Value Range: "| **Fair Value Range** | $250 – $420 – $620 |"  →  low, mid, high
FV_RANGE_RE = re.compile(
    rf"\|\s*\*?\*?Fair Value Range\*?\*?\s*\|\s*{MONEY}{DASH}{MONEY}{DASH}{MONEY}",
    re.IGNORECASE,
)
# Fallback: just Fair Value Mid e.g. "| Fair Value Mid | $420 |"
FV_MID_RE = re.compile(rf"\|\s*(?:\*?\*?)Fair Value Mid(?:\*?\*?)\s*\|\s*{MONEY}", re.IGNORECASE)

# Catalyst table row: "| 2026-06-25 (est.) | Q3 FY2026 财报 | ... |"
# Group 1 = date string (yyyy-mm-dd portion); rest of the row captured loose
CATALYST_ROW_RE = re.compile(
    r"^\|\s*(\d{4}-\d{2}-\d{2})(?:\s*\([^)]*\))?\s*\|\s*([^|]+?)\s*\|(.*)$",
    re.MULTILINE,
)

# Pillar title (bold inline): "**Thesis Pillar 1: 基本面强劲...**"
# also tolerates "**Pillar 1: ...**" / "**支柱 1: ...**"
PILLAR_TITLE_RE = re.compile(
    r"\*\*(?:Thesis\s*)?(?:Pillar|支柱)\s*\d+\s*[:：]\s*([^\n*]+?)\*\*",
    re.IGNORECASE,
)


def parse_args():
    p = argparse.ArgumentParser(description="Extract signals from latest memos")
    p.add_argument("--tickers", required=True, help="Comma-separated tickers, e.g. NVDA,GOOGL,MU")
    p.add_argument("--max-catalyst-days", type=int, default=30, help="Only include catalysts within N days")
    p.add_argument("--research-dir", default=str(RESEARCH_DIR), help="Override Research/ root")
    p.add_argument("--json", action="store_true", help="Output JSON (default if no other flag)")
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return p.parse_args()


def find_latest_memo(research_dir: Path, ticker: str) -> Path | None:
    """Find the most-recently-modified *_memo.md under Research/{ticker}/.

    Excludes quick-check, data_contract, and any file under sub-dirs.
    """
    tdir = research_dir / ticker
    if not tdir.is_dir():
        return None
    candidates = [
        p for p in tdir.glob("*.md")
        if p.is_file()
        and p.name.endswith("_memo.md")
        and "quick-check" not in p.name
        and not p.name.startswith("data_contract")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _section_slice(text: str, start_re: re.Pattern, next_re: re.Pattern | None) -> str:
    m = start_re.search(text)
    if not m:
        return ""
    start = m.end()
    if next_re:
        m2 = next_re.search(text, start)
        end = m2.start() if m2 else len(text)
    else:
        end = len(text)
    return text[start:end]


def _money(s: str) -> float:
    return float(s.replace(",", ""))


def extract_pillars(sec1_text: str, limit: int = 3) -> list[str]:
    """Extract pillar titles from §1.

    Memo format: **Thesis Pillar N: <one-line summary>** then paragraph.
    We capture the title line (which IS the pillar thesis in one sentence).
    """
    pillars: list[str] = []
    for m in PILLAR_TITLE_RE.finditer(sec1_text):
        title = m.group(1).strip().rstrip("。.,;；")
        if title:
            pillars.append(title)
        if len(pillars) >= limit:
            break
    return pillars


def extract_zones(text: str) -> dict:
    """Extract Buy Zone, Trim Zone, Fair Value (low/mid/high)."""
    out = {"buy_zone": None, "trim_zone": None, "fair_value_low": None, "fair_value_mid": None, "fair_value_high": None}
    if (m := BUY_ZONE_RE.search(text)):
        out["buy_zone"] = [_money(m.group(1)), _money(m.group(2))]
    if (m := TRIM_ZONE_RE.search(text)):
        out["trim_zone"] = [_money(m.group(1)), _money(m.group(2))]
    if (m := FV_RANGE_RE.search(text)):
        out["fair_value_low"] = _money(m.group(1))
        out["fair_value_mid"] = _money(m.group(2))
        out["fair_value_high"] = _money(m.group(3))
    elif (m := FV_MID_RE.search(text)):
        out["fair_value_mid"] = _money(m.group(1))
    return out


def extract_catalysts(sec21_text: str, max_days: int) -> list[dict]:
    today = date.today()
    cutoff = today + timedelta(days=max_days)
    cats: list[dict] = []
    for m in CATALYST_ROW_RE.finditer(sec21_text):
        date_s, event, rest = m.group(1), m.group(2).strip(), m.group(3)
        try:
            d = datetime.strptime(date_s, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < today or d > cutoff:
            continue
        # Optional 3rd column = type/importance; the row is variable
        rest_cols = [c.strip() for c in rest.split("|") if c.strip()]
        importance = rest_cols[0] if rest_cols else ""
        cats.append({
            "date": date_s,
            "event": event,
            "importance": importance,
        })
    cats.sort(key=lambda c: c["date"])
    return cats[:2]  # top 2 nearest


def load_one(ticker: str, research_dir: Path, max_days: int) -> dict:
    memo = find_latest_memo(research_dir, ticker)
    if memo is None:
        return {"_status": "no_memo"}

    text = memo.read_text(encoding="utf-8", errors="replace")

    sec1_text = _section_slice(text, SEC1_RE, re.compile(r"^#{1,3}\s+", re.MULTILINE))
    sec20_text = _section_slice(text, SEC20_RE, SEC21_RE)
    sec21_text = _section_slice(text, SEC21_RE, None)

    zones = extract_zones(text)  # search whole doc — Executive Summary mirrors §20
    if not zones["buy_zone"] and not zones["trim_zone"]:
        # try §20 specifically
        zones = extract_zones(sec20_text)

    return {
        "_status": "ok",
        "memo_path": str(memo.relative_to(REPO_ROOT)) if memo.is_relative_to(REPO_ROOT) else str(memo),
        "memo_date": memo.stem.split("_memo")[0],  # e.g. "2026-05-10"
        "memo_mtime": datetime.fromtimestamp(memo.stat().st_mtime).isoformat(timespec="seconds"),
        "pillars": extract_pillars(sec1_text or text),
        **zones,
        "catalysts": extract_catalysts(sec21_text or text, max_days),
    }


def main() -> int:
    args = parse_args()
    research_dir = Path(args.research_dir)
    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]

    out = {t: load_one(t, research_dir, args.max_catalyst_days) for t in tickers}

    indent = 2 if args.pretty else None
    json.dump(out, sys.stdout, ensure_ascii=False, indent=indent, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
