#!/usr/bin/env python3
"""
validate_data_contract.py — lint a filled Data Contract file.

Enforces the data-provenance rules established by:
- PR #4 (2026-05-18): no estimated data, no "~/约/approximately" phrasing
- PR #7 (2026-05-19): Phase B Data Provenance Audit, Pull Date = research day

Usage:
    python3 validate_data_contract.py <path-to-data_contract.md>
    python3 validate_data_contract.py Research/CRWV/data_contract.md

Exit codes:
    0 — all checks passed
    1 — one or more violations found (details printed)
    2 — file not found or parse error

Designed to be called from:
- data-fetch SKILL after Data Contract generation (block downstream if fail)
- stock-research SKILL Step 9 Phase B (second-layer check)
- pre-commit hook (optional)
- CI lint workflow (optional)
"""

import argparse
import datetime as _dt
import pathlib
import re
import sys

BANNED_NUMERIC_PHRASES = [
    "~",
    "约 ",
    "约$",
    "approximately",
    "approx.",
    "市场近似",
    "市场公开近似",
    "业界常见",
    "estimated",
    "rough estimate",
    "ballpark",
]

PEER_SECTION_HEADING = re.compile(r"^##\s+(?:\d+\.?\s+)?Peer Data\b", re.MULTILINE)
SECTION_HEADING = re.compile(r"^##\s+", re.MULTILINE)
TABLE_ROW = re.compile(r"^\|.+\|\s*$")
DATE_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def _extract_section(text: str, heading_re: re.Pattern) -> "str | None":
    match = heading_re.search(text)
    if not match:
        return None
    start = match.start()
    after = SECTION_HEADING.search(text, match.end())
    end = after.start() if after else len(text)
    return text[start:end]


def _table_rows(section: str) -> "list[str]":
    """Return data rows only (excludes header line and separator). Walks each
    markdown table within the section: the row immediately preceding a
    separator `|---|---|` line is the header and must also be skipped."""
    rows: "list[str]" = []
    pending_header = None
    in_data = False
    for line in section.splitlines():
        line = line.rstrip()
        if not TABLE_ROW.match(line):
            # blank line / non-table text ends the current table
            pending_header = None
            in_data = False
            continue
        if set(line.replace("|", "").strip()) <= set("-: "):
            # separator → previous line was the header (drop it), now in data
            pending_header = None
            in_data = True
            continue
        if not in_data:
            # candidate header; will be discarded if separator follows
            pending_header = line
            continue
        rows.append(line)
    return rows


def _check_banned_phrases(text: str) -> "list[str]":
    violations = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        # Skip rule-definition lines (the template itself documents the banned words)
        if "MANDATORY" in line or "must equal" in line or "banned" in line.lower():
            continue
        # Numeric-context heuristic: the phrase is suspicious only when next to
        # a digit, $/¥/%, or appears inside a table cell.
        is_table_cell = "|" in line
        for phrase in BANNED_NUMERIC_PHRASES:
            if phrase in line and (is_table_cell or re.search(r"\d|[$%¥]", line)):
                # tilde inside hyperlink anchors (#section-name) is OK
                if phrase == "~" and re.search(r"\(#[\w-]+\)", line):
                    continue
                violations.append(
                    f"L{i}: banned phrase {phrase!r} in numeric/table context: {line.strip()!r}"
                )
                break
    return violations


def _check_peer_section(text: str, today: _dt.date, mode: str) -> "list[str]":
    """Validate the `## Peer Data` section.

    The `mode` parameter controls whether this section is required:

    - `full`       — initial target fetch. `## Peer Data` may be present
                     but empty (no data rows yet). Section absence is fine
                     too: stock-research will trigger a supplement call
                     after §5a.
    - `quick`      — quick-check path. Peer Data may be absent entirely
                     (quick-check often skips peers).
    - `supplement` — post-supplement validation. Section MUST exist and
                     contain ≥ 5 data rows, every row Pull Date == today.
    """
    violations = []
    section = _extract_section(text, PEER_SECTION_HEADING)
    if section is None:
        if mode == "supplement":
            violations.append(
                "missing required `## Peer Data` section (supplement mode expects it populated)"
            )
        # full / quick: absence is OK
        return violations

    rows = _table_rows(section)

    # In `full` mode at initial generation, the section may be empty
    # (data-fetch wrote the header skeleton; supplement will fill rows).
    # In `quick` mode, peers are optional.
    # Only enforce row-count and per-row checks in `supplement` mode.
    if mode != "supplement":
        return violations

    if len(rows) < 5:
        violations.append(
            f"Peer Data section has only {len(rows)} data row(s); minimum is 5 in supplement mode"
        )
    if len(rows) > 8:
        # 8 is the recommended max for Comps median computation; extra rows
        # beyond 8 are tolerated as audit-retention (excluded peers stay in
        # the Contract per append-only semantics) but flagged as a warning.
        violations.append(
            f"Peer Data section has {len(rows)} data rows; recommended max for Comps is 8. "
            f"Extra rows must be documented as excluded in §20a 'Outlier Exclusions'."
        )

    for row in rows:
        cells = [c.strip() for c in row.split("|")[1:-1]]
        if not cells:
            continue

        # Pull Date must be the last column and must equal today
        last_cell = cells[-1] if cells else ""
        if not last_cell:
            violations.append(f"row missing Pull Date: {row.strip()!r}")
            continue
        if last_cell.lower().startswith("n/a"):
            # explicit unavailability is acceptable per template
            continue
        m = DATE_ISO.search(last_cell)
        if not m:
            violations.append(
                f"row Pull Date column is not ISO-format YYYY-MM-DD: {last_cell!r}"
            )
            continue
        try:
            pull_date = _dt.date.fromisoformat(m.group(1))
        except ValueError:
            violations.append(f"row Pull Date unparseable: {last_cell!r}")
            continue
        if pull_date != today:
            violations.append(
                f"row Pull Date {pull_date.isoformat()} != research day "
                f"{today.isoformat()} (re-pull required): {row.strip()!r}"
            )

        # Source column should be second-to-last and non-empty
        if len(cells) >= 2:
            source = cells[-2]
            if not source or source.lower() in {"", "—", "tbd", "n/a"}:
                violations.append(f"row Source column empty: {row.strip()!r}")

    return violations


def validate(path: pathlib.Path, today: _dt.date, mode: str) -> "list[str]":
    if not path.exists():
        return [f"file not found: {path}"]
    text = path.read_text(encoding="utf-8")

    violations: "list[str]" = []
    violations.extend(_check_banned_phrases(text))
    violations.extend(_check_peer_section(text, today, mode))
    return violations


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("path", help="path to a filled Data Contract file")
    parser.add_argument(
        "--today",
        help="override research day (YYYY-MM-DD); default: system today",
    )
    parser.add_argument(
        "--mode",
        choices=("full", "quick", "supplement"),
        default="supplement",
        help=(
            "data-fetch invocation mode the Contract represents. "
            "`supplement` (default) requires `## Peer Data` to be populated; "
            "`full`/`quick` allow it to be absent or empty."
        ),
    )
    args = parser.parse_args(argv)

    today = (
        _dt.date.fromisoformat(args.today) if args.today else _dt.date.today()
    )
    path = pathlib.Path(args.path)
    try:
        violations = validate(path, today, args.mode)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not violations:
        print(
            f"OK: {path} passes all data-provenance checks "
            f"(research day={today.isoformat()}, mode={args.mode})"
        )
        return 0

    print(f"FAIL: {len(violations)} violation(s) in {path} (mode={args.mode})")
    for v in violations:
        print(f"  - {v}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
