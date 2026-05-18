#!/usr/bin/env python3
"""
validate_memo_format.py — lint a stock-research memo against template hard constraints.

Catches the failure modes seen on `Research/CRWV/2026-05-19_memo.md` (the memo that
prompted this validator): missing Buy/Trim Zone rows, Chinese-ordinal pillar titles,
and catalyst dates like `2026Q2 报告（预计 8 月）` that downstream parsers can't read.

Hard constraints checked (all required; ALL FAIL on any violation):

  C1. Executive Summary (memo head → first `## §1` boundary) MUST contain BOTH
      a `| Buy Zone | $X – $Y | ... |` row AND a `| Trim Zone | ... |` row.
      (Source: `references/investment_memo.md` Executive Summary template,
       lines 163-167. Required by morning-update / memo_loader downstream.)

  C2. §1 (Thesis Framework) MUST contain ≥3 pillar titles in the format
      `**Thesis Pillar N: <title>**`  or  `**Pillar N: <title>**`.
      N must be an Arabic digit (1, 2, 3, …). Chinese ordinals ("一二三") are
      forbidden — they break memo_loader's pillar regex.
      (Source: template line 294; SKILL.md L114.)

  C3. §21d (Catalysts & Monitoring) MUST contain ≥1 catalyst-table row whose
      first cell is a strict YYYY-MM-DD date (an optional trailing `(est.)`
      and other annotations are OK as long as the YYYY-MM-DD prefix is present).
      Forms like `2026Q2 报告`, `持续`, `2027 上半年` are non-standard and
      cause memo_loader to skip them.
      (Source: template line 626; CRITICAL: this gates morning-update Part 1.)

Exit codes:
  0  — all checks pass
  1  — one or more checks fail; stderr lists violations + repair hints

Usage:
  python3 validate_memo_format.py <memo_path>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Section locators (bilingual; mirror memo_loader.py)
# ---------------------------------------------------------------------------

# Section locators by number only (subtitle can be anything: 论点框架 / Thesis Framework /
# Investment Thesis Framework / 投资论点框架（Thesis Framework）/ etc.).
# (?![0-9]) prevents §1 from swallowing §10/§11/§19 and §2 from swallowing §20/§21.
SEC1_RE = re.compile(r"^#{1,3}\s+(?:§\s*)?1(?![0-9])", re.MULTILINE)
SEC2_RE = re.compile(r"^#{1,3}\s+(?:§\s*)?2(?![0-9])", re.MULTILINE)
SEC21_RE = re.compile(r"^#{1,3}\s+(?:§\s*)?21(?![0-9])", re.MULTILINE)
SEC21D_RE = re.compile(
    r"^#{2,5}\s*21d[:.]?\s",
    re.IGNORECASE | re.MULTILINE,
)
NEXT_HEADER_RE = re.compile(r"^#{1,5}\s+", re.MULTILINE)

# ---------------------------------------------------------------------------
# Constraint regexes
# ---------------------------------------------------------------------------

BUY_ZONE_ROW_RE = re.compile(r"^\|\s*Buy Zone\s*\|", re.IGNORECASE | re.MULTILINE)
TRIM_ZONE_ROW_RE = re.compile(r"^\|\s*Trim Zone\s*\|", re.IGNORECASE | re.MULTILINE)

# Pillar titles — Arabic digit form (PASSING)
PILLAR_ARABIC_RE = re.compile(
    r"\*\*(?:Thesis\s+)?(?:Pillar|支柱)\s+(\d+)\s*[:：]\s*[^\n*]+\*\*",
    re.IGNORECASE,
)
# Pillar titles — Chinese ordinal form (FAILING; reported separately)
PILLAR_CN_ORDINAL_RE = re.compile(
    r"\*\*(?:Thesis\s*)?(?:Pillar|支柱)\s*([一二三四五六七八九十]+)\s*[:：]\s*[^\n*]+\*\*"
)

# Catalyst table row, first cell strictly starts with YYYY-MM-DD
CATALYST_GOOD_DATE_RE = re.compile(
    r"^\|\s*(\d{4}-\d{2}-\d{2})(?:\s*\([^)]*\))?\s*\|",
    re.MULTILINE,
)
# Common non-standard date heads to flag explicitly
CATALYST_BAD_HEAD_RE = re.compile(
    r"^\|\s*("
    r"\d{4}\s*Q[1-4][^|]*|"           # 2026Q2 报告
    r"\d{4}\s*年?\s*[上下]\s*半年|"   # 2027 上半年
    r"\d{4}\s*年?\s*[Qq一二三四]季度|"
    r"持续|"
    r"ongoing|"
    r"continuously"
    r")[^|]*\|",
    re.IGNORECASE | re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Section slicing
# ---------------------------------------------------------------------------

def _slice_between(text: str, start_re: re.Pattern, end_re: re.Pattern | None) -> str:
    m = start_re.search(text)
    if not m:
        return ""
    start = m.end()
    if end_re:
        m2 = end_re.search(text, start)
        end = m2.start() if m2 else len(text)
    else:
        end = len(text)
    return text[start:end]


def get_executive_summary(text: str) -> str:
    """Memo head → first '## §1' boundary."""
    m = SEC1_RE.search(text)
    return text[: m.start()] if m else text


def get_section_1(text: str) -> str:
    """§1 → §2 (or end if §2 missing)."""
    return _slice_between(text, SEC1_RE, SEC2_RE)


def get_section_21d(text: str) -> str:
    """§21d → next ## header (or end). Fallback: full §21 if 21d subheader missing."""
    m21d = SEC21D_RE.search(text)
    if m21d:
        start = m21d.end()
        # find next ## or ### header AFTER 21d to bound the slice
        m_next = NEXT_HEADER_RE.search(text, start)
        return text[start: m_next.start() if m_next else len(text)]
    # fallback: full §21 section
    return _slice_between(text, SEC21_RE, NEXT_HEADER_RE) if SEC21_RE.search(text) else ""


# ---------------------------------------------------------------------------
# Constraint checks
# ---------------------------------------------------------------------------

def check_c1_zones(text: str) -> list[str]:
    es = get_executive_summary(text)
    errs: list[str] = []
    if not BUY_ZONE_ROW_RE.search(es):
        errs.append(
            "C1a: Executive Summary 缺少 `| Buy Zone | $X – $Y | ... |` 行。"
            "\n    修复：参考 references/investment_memo.md L165 模板，在 Executive Summary 的 Zone 表加上 Buy Zone 行"
        )
    if not TRIM_ZONE_ROW_RE.search(es):
        errs.append(
            "C1b: Executive Summary 缺少 `| Trim Zone | ... |` 行。"
            "\n    修复：参考 references/investment_memo.md L167 模板，在 Executive Summary 的 Zone 表加上 Trim Zone 行"
        )
    return errs


def check_c2_pillars(text: str) -> list[str]:
    sec1 = get_section_1(text)
    if not sec1:
        return ["C2: 找不到 §1 论点框架/Thesis Framework section。"]
    errs: list[str] = []

    cn_matches = list(PILLAR_CN_ORDINAL_RE.finditer(sec1))
    if cn_matches:
        examples = ", ".join(m.group(0)[:60] for m in cn_matches[:3])
        errs.append(
            f"C2a: §1 含 {len(cn_matches)} 个中文序数 pillar 标题（如：{examples}…）。"
            "\n    修复：把 `**支柱一：...**` 改为 `**Thesis Pillar 1: ...**`（必须阿拉伯数字；中文序数会让 memo_loader 抓不到）"
        )

    arabic_matches = list(PILLAR_ARABIC_RE.finditer(sec1))
    if len(arabic_matches) < 3:
        errs.append(
            f"C2b: §1 仅检测到 {len(arabic_matches)} 个合规 pillar 标题，需 ≥3 个 `**(Thesis )?Pillar N: ...**` 形态。"
            "\n    修复：参考 references/investment_memo.md L291-294 模板，§1 必须包含至少 3 个 Thesis Pillar"
        )
    return errs


def check_c3_catalyst_dates(text: str) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings).

    FAIL only if §21d missing entirely or has 0 YYYY-MM-DD rows. Mixed
    formatting (some YYYY-MM-DD + some quarter labels like `2026 Q3`) is a
    WARN — quarter dates are reasonable when company hasn't pinned an exact
    earnings date yet, and memo_loader simply ignores those rows.
    """
    sec21d = get_section_21d(text)
    if not sec21d:
        return (["C3: 找不到 §21d Catalysts & Monitoring section。"], [])

    good = list(CATALYST_GOOD_DATE_RE.finditer(sec21d))
    bad = list(CATALYST_BAD_HEAD_RE.finditer(sec21d))

    errs: list[str] = []
    warns: list[str] = []

    if len(good) < 1:
        msg = "C3a: §21d 催化剂表内无任何 `| YYYY-MM-DD ... |` 起头的行（至少需要 1 行）。"
        if bad:
            examples = "; ".join(m.group(0).strip()[:50] for m in bad[:3])
            msg += f"\n    检测到 {len(bad)} 行非标日期格式（如：{examples}）— 这些会让 memo_loader 跳过"
        msg += "\n    修复：把 `2026Q2 报告（预计 8 月）` 等改为 `2026-08-15 (est.)` 形态；参考 references/investment_memo.md L626 模板"
        errs.append(msg)
    elif bad:
        examples = "; ".join(m.group(0).strip()[:50] for m in bad[:3])
        warns.append(
            f"C3b (WARN): §21d 含 {len(good)} 行合规日期 + {len(bad)} 行季度/非标日期（如：{examples}）。"
            "\n    建议：远期催化剂未定具体日期时也可写 `2026-08-15 (Q2 est.)` — memo_loader 会按日期取最近条目"
        )
    return errs, warns


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="Validate stock-research memo format")
    p.add_argument("memo_path", help="Path to *_memo.md")
    p.add_argument("--quiet", action="store_true", help="Only exit code; suppress stderr details")
    args = p.parse_args()

    path = Path(args.memo_path)
    if not path.is_file():
        print(f"[validator] file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8", errors="replace")

    all_errs: list[str] = []
    all_warns: list[str] = []
    all_errs += check_c1_zones(text)
    all_errs += check_c2_pillars(text)
    c3_errs, c3_warns = check_c3_catalyst_dates(text)
    all_errs += c3_errs
    all_warns += c3_warns

    if not all_errs:
        if not args.quiet:
            print(f"✅ {path.name} 格式合规 (C1 Buy/Trim Zone / C2 Pillars / C3 Catalyst dates 全部通过)")
            for w in all_warns:
                print(f"\n  ⚠️  {w}")
        return 0

    if not args.quiet:
        print(f"❌ {path.name} 有 {len(all_errs)} 项格式违规：", file=sys.stderr)
        for i, err in enumerate(all_errs, 1):
            print(f"\n  [{i}] {err}", file=sys.stderr)
        for w in all_warns:
            print(f"\n  ⚠️  {w}", file=sys.stderr)
        print(
            f"\n参考模板：investment-plugin/skills/stock-research/references/investment_memo.md\n"
            f"如果你刚改完 memo，重跑：python3 {sys.argv[0]} {path}",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
