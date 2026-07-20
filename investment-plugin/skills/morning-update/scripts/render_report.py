#!/usr/bin/env python3
"""
render_report.py — pure rendering: stdin JSON (schema v2) → stdout Markdown.

Briefing layout (10-minute read):
  Part 1 — 必读文章     (must_read: Citrini 等 must_push 源 + worth_reading 精选)
  Part 2 — 新闻与观点   (news_curated 5-8 条)
  Part 3 — 今日发现     (discovery, 必须带 source_articles)
  Part 4 — 交易信号     (CONDITIONAL — 只在有 buy/trim 信号时渲染)

Input contract (see morning-update SKILL.md §Step 7):
  {
    "date": "2026-07-14",
    "fetched_at": "2026-07-14T08:00:00+08:00",
    "must_read":     [{title, url, source, summary_cn, watchlist_link_cn}],
    "worth_reading": [{title, url, source, why_cn}],
    "news_curated":  [{title, url, source, related, fact_cn, opinion_cn,
                       stance: "confirm"|"challenge"|"neutral"}],
    "discovery": {type, name, tickers, what_cn, why_cn, difference_cn,
                  next_step_cn, source_articles: [{title, url}]}
                 | {"none_today": true, "scanned_note_cn": "..."},
    "positions": [...],          // from portfolio-fetch (optional)
    "watchlist": [...],          // from watchlist.json + current_price
    "memos": { TICKER: memo_loader_output },
    "portfolio_unavailable": false,
    "stats": {"news_scanned": 668, "news_kept": 8}
  }

Output: markdown to stdout. No network, no MCP, no file IO except stdout.
Part headers MUST keep the "## Part N —" prefix — push_telegram.py splits on it.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime

E_BUY = "🟢"
E_TRIM = "🔴"
E_ERROR = "❌"

# stance emoji 放条目行首（Telegram 手机端一眼可扫）；neutral 用中性方块
STANCE_MARK = {"confirm": "✅", "challenge": "⚠️", "neutral": "▫️"}


# ---------------------------------------------------------------------------
# Zone signals (migrated from v1)
# ---------------------------------------------------------------------------

def zone_status(price, memo) -> str:
    """'no_memo' | 'no_price' | 'in_buy' | 'below_buy' | 'normal' |
       'in_trim' | 'above_trim'."""
    if not memo or memo.get("_status") != "ok":
        return "no_memo"
    if price is None or price <= 0:
        return "no_price"
    buy = memo.get("buy_zone")
    trim = memo.get("trim_zone")
    if buy and buy[0] <= price <= buy[1]:
        return "in_buy"
    if buy and price < buy[0]:
        return "below_buy"
    if trim and trim[0] <= price <= trim[1]:
        return "in_trim"
    if trim and price > trim[1]:
        return "above_trim"
    return "normal"


# watchlist notes fallback: "买入区 $187–215" / "Buy Zone $187-215"
MONEY = r"\$\s*([\d,]+(?:\.\d+)?)"
DASH = r"[\s]*[–—-][\s]*"
NOTES_BUY_RE = re.compile(rf"(?:买入区|Buy Zone)\s*{MONEY}{DASH}\$?\s*([\d,]+(?:\.\d+)?)", re.IGNORECASE)


def zone_from_notes(notes: str):
    """Approximate buy zone parsed from watchlist notes. Returns pseudo-memo."""
    if not notes:
        return None
    m = NOTES_BUY_RE.search(notes)
    if not m:
        return None
    low = float(m.group(1).replace(",", ""))
    high = float(m.group(2).replace(",", ""))
    return {"_status": "ok", "_from_notes": True, "buy_zone": [low, high], "trim_zone": None}


def _strip_market_prefix(code: str) -> str:
    return code.split(".", 1)[1] if "." in code else code


def _zone_str(zone) -> str:
    if not zone:
        return "—"
    return f"${zone[0]:.2f}–${zone[1]:.2f}"


def _midpoint(zone):
    if not zone or len(zone) != 2:
        return None
    return (zone[0] + zone[1]) / 2


def build_signals(data: dict):
    """Return (buy_signals, trim_signals) — only actionable ones.

    buy_signals:  watchlist (non-holding) tickers in/below buy zone
    trim_signals: holding tickers in/above trim zone
    Holdings entering their own buy zone are also reported (加仓 case) in buy_signals.
    """
    positions = data.get("positions") or []
    watchlist = data.get("watchlist") or []
    memos = data.get("memos") or {}
    pos_idx = {_strip_market_prefix(p["code"]): p for p in positions if p.get("code")}

    buy_signals, trim_signals = [], []

    for tkr, p in pos_idx.items():
        memo = memos.get(tkr)
        price = (p.get("snapshot") or {}).get("last_price") or p.get("nominal_price")
        st = zone_status(price, memo)
        if st in ("in_trim", "above_trim"):
            trim_signals.append({"ticker": tkr, "price": price, "memo": memo, "status": st, "holding": True})
        elif st in ("in_buy", "below_buy"):
            buy_signals.append({"ticker": tkr, "price": price, "memo": memo, "status": st, "holding": True})

    for w in watchlist:
        tkr = w["ticker"]
        if tkr in pos_idx:
            continue
        memo = memos.get(tkr)
        if not memo or memo.get("_status") != "ok":
            memo = zone_from_notes(w.get("notes", "")) or memo
        price = w.get("current_price")
        st = zone_status(price, memo)
        if st in ("in_buy", "below_buy"):
            buy_signals.append({"ticker": tkr, "price": price, "memo": memo, "status": st, "holding": False})

    return buy_signals, trim_signals


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------

def render_part1(data: dict) -> str:
    L = ["## Part 1 — 📚 必读文章", ""]
    must = data.get("must_read") or []
    worth = data.get("worth_reading") or []

    for m in must:
        L.append(f"### 📌 {m.get('source', 'Must-read')}")
        L.append(f"**[{m.get('title', '')}]({m.get('url', '')})**")
        if m.get("summary_cn"):
            L.append(f"- {m['summary_cn']}")
        if m.get("watchlist_link_cn"):
            L.append(f"- 与 watchlist 的关联：{m['watchlist_link_cn']}")
        L.append("")

    if worth:
        L.append("### 值得读")
        L.append("")
        for w in worth:
            L.append(f"- **[{w.get('title', '')}]({w.get('url', '')})**")
            if w.get("why_cn"):
                L.append(f"  - {w['why_cn']}（{w.get('source', '')}）")
            L.append("")

    if not must and not worth:
        L.append("_今日无必读文章（Citrini 等 must-push 源无新文，精选池为空）_")
        L.append("")
    return "\n".join(L)


def render_part2(data: dict) -> str:
    L = ["## Part 2 — 📰 新闻与观点", ""]
    news = data.get("news_curated") or []
    if news:
        L.append(f"### 重点新闻（{len(news)} 条）")
        L.append("")
        for n in news:
            related = n.get("related", "")
            mark = STANCE_MARK.get(n.get("stance", "neutral"), "▫️")
            # stance emoji 行首 + 标题独占一行；来源并入观点行，避免标题行过长换行
            head = f"- {mark} **[{n.get('title', '')}]({n.get('url', '')})**"
            if related:
                head += f" 「{related}」"
            L.append(head)
            if n.get("fact_cn"):
                L.append(f"  - 事实：{n['fact_cn']}")
            if n.get("opinion_cn"):
                L.append(f"  - 观点：{n['opinion_cn']}")
            L.append("")
    else:
        L.append("_今日无 thesis-relevant 新闻_")
        L.append("")
    return "\n".join(L)


def render_part3(data: dict) -> str:
    L = ["## Part 3 — 💡 今日发现", ""]
    d = data.get("discovery")
    if not d or d.get("none_today"):
        note = (d or {}).get("scanned_note_cn", "")
        L.append(f"_今日无新发现。{note}_".rstrip())
        L.append("")
        return "\n".join(L)

    tickers = "、".join(d.get("tickers") or []) or "—"
    kind = "概念" if d.get("type") == "concept" else "标的"
    L.append(f"**{d.get('name', '')}**（{kind} · 相关标的：{tickers}）")
    if d.get("what_cn"):
        L.append(f"- 是什么：{d['what_cn']}")
    if d.get("why_cn"):
        L.append(f"- 为什么有潜力：{d['why_cn']}")
    if d.get("difference_cn"):
        L.append(f"- 与现有 watchlist 的差异：{d['difference_cn']}")
    arts = d.get("source_articles") or []
    if arts:
        links = " / ".join(f"[{a.get('title', 'link')}]({a['url']})" for a in arts if a.get("url"))
        L.append(f"- 来源文章：{links}")
    if d.get("next_step_cn"):
        L.append(f"- 下一步：{d['next_step_cn']}")
    L.append("")
    return "\n".join(L)


def render_part4(buy_signals: list, trim_signals: list) -> str:
    """CONDITIONAL — caller only invokes when signals exist."""
    L = ["## Part 4 — 📊 交易信号", ""]

    if buy_signals:
        L.append(f"### {E_BUY} Buy Zone")
        for s in buy_signals:
            memo = s["memo"] or {}
            zone = memo.get("buy_zone")
            mid = _midpoint(zone)
            price_s = f"${s['price']:.2f}" if s.get("price") else "—"
            role = "持仓加仓" if s["holding"] else "watchlist 建仓"
            line = f"- **{s['ticker']}** {price_s} · Buy Zone {_zone_str(zone)} · {role}"
            if s["status"] == "below_buy":
                line += " · 已低于区间下沿，可市价分批"
            elif mid:
                line += f" · 建议限价 ${mid:.2f}"
            if memo.get("_from_notes"):
                line += " *（zone 来自 notes，非正式 memo）*"
            L.append(line)
        L.append("")

    if trim_signals:
        L.append(f"### {E_TRIM} Trim / Sell")
        for s in trim_signals:
            memo = s["memo"] or {}
            zone = memo.get("trim_zone")
            price_s = f"${s['price']:.2f}" if s.get("price") else "—"
            if s["status"] == "above_trim":
                action = "已超越 Trim Zone，考虑全部卖出（市价或现价限价，勿用 zone 价挂单）"
            else:
                action = "建议减仓 25-50%"
            line = f"- **{s['ticker']}** {price_s} · Trim Zone {_zone_str(zone)} · {action}"
            if zone and s["status"] == "in_trim":
                line += f" · 挂单参考 ${zone[0]:.2f}（zone 下沿）"
            L.append(line)
        L.append("")

    return "\n".join(L)


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

def render(data: dict) -> str:
    buy_signals, trim_signals = build_signals(data)

    date_s = data.get("date") or date.today().isoformat()
    fetched = data.get("fetched_at") or datetime.now().isoformat(timespec="seconds")

    L = [f"# {date_s} Morning Update", ""]
    if data.get("portfolio_unavailable"):
        L.append(f"{E_ERROR} _持仓数据不可用（OpenD 未启动）— 交易信号仅覆盖 watchlist_")
        L.append("")
    L.append(render_part1(data))
    L.append("---")
    L.append("")
    L.append(render_part2(data))
    L.append("---")
    L.append("")
    L.append(render_part3(data))
    if buy_signals or trim_signals:
        L.append("---")
        L.append("")
        L.append(render_part4(buy_signals, trim_signals))
    L.append("---")
    L.append("")
    stats = data.get("stats") or {}
    tail = f"_生成于 {fetched}"
    if stats.get("news_scanned") is not None:
        tail += f" · 扫描 {stats['news_scanned']} 条 → 保留 {stats.get('news_kept', '—')} 条"
    tail += "_"
    L.append(tail)
    return "\n".join(L)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"# Morning Update — INPUT ERROR\n\n{E_ERROR} Input JSON parse failed: {e}", file=sys.stderr)
        return 1
    sys.stdout.write(render(data))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
