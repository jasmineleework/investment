#!/usr/bin/env python3
"""
render_report.py — pure rendering: stdin JSON → stdout Markdown.

Input contract (see morning-update SKILL.md §Step 5):
  {
    "date": "2026-05-19",
    "fetched_at": "2026-05-19T08:00:00+08:00",
    "portfolio_unavailable": false,
    "funds": {...},                  // from portfolio-fetch
    "summary": {...},                // from portfolio-fetch
    "positions": [...],              // from portfolio-fetch positions[]
    "watchlist": [...],              // from watchlist.json + live price
    "memos": { TICKER: memo_loader_output },
    "news": { TICKER: [{title, url, opinion}] },
    "ratings": { TICKER: "Buy → Strong Buy (..., 2d)" },
    "filings": { TICKER: [{date, summary, url}] },
    "focus": null | "NVDA"
  }

Output: markdown to stdout. No network, no MCP, no file IO except stdout.

Field discipline (HARD): P&L MUST use unrealized_pl + pl_ratio_avg_cost.
NEVER pl_val / pl_ratio / cost_price / diluted_cost.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from typing import Any

# Emoji status taxonomy
E_BUY = "⚡"
E_TRIM = "⚠️"
E_ABOVE = "🚫"
E_NORMAL = "✅"
E_NO_MEMO = "📌"
E_ERROR = "❌"
E_TOP = "🎯"


# ---------------------------------------------------------------------------
# Signal classification
# ---------------------------------------------------------------------------

def zone_status(price: float | None, memo: dict | None) -> str:
    """Return one of: 'no_memo' | 'no_price' | 'in_buy' | 'below_buy' |
       'normal' | 'in_trim' | 'above_trim'."""
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


STATUS_TO_EMOJI = {
    "in_buy": E_BUY,
    "below_buy": E_BUY,
    "in_trim": E_TRIM,
    "above_trim": E_ABOVE,
    "normal": E_NORMAL,
    "no_memo": E_NO_MEMO,
    "no_price": E_NO_MEMO,
}

STATUS_TO_LABEL = {
    "in_buy": "进入 Buy Zone",
    "below_buy": "低于 Buy Zone",
    "in_trim": "进入 Trim Zone",
    "above_trim": "Above Trim Zone",
    "normal": "正常",
    "no_memo": "未做研究",
    "no_price": "无现价",
}

ACTION_BY_STATUS = {
    "in_buy": "建议加仓 1-2% / 新建仓 3-5%",
    "below_buy": "深度安全边际，建议加仓 1-2%",
    "in_trim": "建议减仓 25-50%",
    "above_trim": "考虑全部卖出",
    "normal": "持有",
    "no_memo": "未做研究，无 action（请 `/research <ticker>`）",
    "no_price": "无现价数据",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_money(v) -> str:
    if v is None or v == "":
        return "—"
    try:
        fv = float(v)
    except (ValueError, TypeError):
        return str(v)
    if abs(fv) >= 1e9:
        return f"${fv/1e9:.2f}B"
    if abs(fv) >= 1e6:
        return f"${fv/1e6:.2f}M"
    if abs(fv) >= 1000:
        return f"${fv:,.2f}"
    return f"${fv:.2f}"


def _fmt_pct(v, digits: int = 1) -> str:
    if v is None or v == "":
        return "—"
    try:
        return f"{float(v):+.{digits}f}%"
    except (ValueError, TypeError):
        return str(v)


def _strip_market_prefix(code: str) -> str:
    return code.split(".", 1)[1] if "." in code else code


def _index_positions(positions: list) -> dict:
    """Return {ticker_without_prefix: position}."""
    return {_strip_market_prefix(p["code"]): p for p in positions if p.get("code")}


def _zone_str(zone) -> str:
    if not zone:
        return "—"
    return f"${zone[0]:.2f}–${zone[1]:.2f}"


def _midpoint(zone) -> float | None:
    if not zone or len(zone) != 2:
        return None
    return (zone[0] + zone[1]) / 2


# ---------------------------------------------------------------------------
# Top Call election
# ---------------------------------------------------------------------------

def elect_top_call(data: dict, position_signals: dict, watchlist_signals: dict) -> str:
    """Priority: in_trim > in_buy (holding) > entered_buy_zone (watching) >
       catalyst ≤30d on largest holding > overnight challenge > default."""
    # 1. in_trim (most urgent)
    for tkr, sig in position_signals.items():
        if sig["status"] == "in_trim":
            zone = sig["memo"].get("trim_zone") if sig.get("memo") else None
            return f"**{tkr} 进入 Trim Zone ({_zone_str(zone)})** — 建议减仓 25-50%"
        if sig["status"] == "above_trim":
            return f"**{tkr} 已超越 Trim Zone** — 考虑全部卖出"

    # 2. in_buy on holdings
    for tkr, sig in position_signals.items():
        if sig["status"] == "in_buy":
            zone = sig["memo"].get("buy_zone")
            return f"**{tkr} 进入 Buy Zone ({_zone_str(zone)})** — 建议加仓 1-2%"

    # 3. watchlist entered Buy Zone
    for tkr, sig in watchlist_signals.items():
        if sig["status"] == "in_buy" or sig["status"] == "below_buy":
            zone = sig["memo"].get("buy_zone") if sig.get("memo") else None
            mid = _midpoint(zone)
            return (
                f"**Watchlist: {tkr} 已进入 Buy Zone ({_zone_str(zone)})** — "
                f"准备挂限价 ${mid:.2f}" if mid else
                f"**Watchlist: {tkr} 已进入 Buy Zone**"
            )

    # 4. nearest catalyst across universe
    all_catalysts = []
    for tkr, sig in {**position_signals, **watchlist_signals}.items():
        memo = sig.get("memo") or {}
        for c in memo.get("catalysts") or []:
            all_catalysts.append((c["date"], tkr, c["event"]))
    if all_catalysts:
        all_catalysts.sort(key=lambda x: x[0])
        d, tkr, ev = all_catalysts[0]
        return f"**{tkr} 催化剂临近：{d} {ev}**"

    # 5. overnight challenge
    for tkr, items in (data.get("news") or {}).items():
        for n in items or []:
            if n.get("opinion") == "challenge":
                return f"**{tkr} 隔夜新闻可能冲击 thesis** — 见 Part 1 详情"

    return "隔夜无重大变化，维持现有仓位"


# ---------------------------------------------------------------------------
# Part 1 — 今日关注
# ---------------------------------------------------------------------------

def render_part1(data: dict, position_signals: dict, watchlist_signals: dict) -> str:
    L = ["## Part 1 — 今日关注", ""]

    pos_signals = position_signals
    wl_signals = watchlist_signals

    def render_entry(tkr: str, sig: dict, kind: str) -> list:
        memo = sig.get("memo") or {}
        emoji = STATUS_TO_EMOJI.get(sig["status"], E_NO_MEMO)
        label = STATUS_TO_LABEL.get(sig["status"], "")
        name = sig.get("name", "")
        lines = [f"- **{tkr}** · {kind} · {emoji} {label}"]

        # 催化剂
        cats = memo.get("catalysts") or []
        if cats:
            top = cats[0]
            lines.append(f"  - 催化剂：{top['date']} {top['event']}")
            if top.get("importance"):
                lines[-1] += f" ({top['importance']})"
        else:
            lines.append("  - 催化剂：无 30 日内催化剂")

        # 重点支柱
        pillars = memo.get("pillars") or []
        if pillars:
            lines.append(f"  - 重点支柱：{pillars[0]}")
        elif memo.get("_status") == "no_memo":
            lines.append(f"  - 重点支柱：{E_NO_MEMO} 未做研究")

        # 隔夜新闻 (max 2 to keep mobile-readable)
        news = (data.get("news") or {}).get(tkr) or []
        keep = [n for n in news if n.get("opinion") in ("confirm", "challenge")][:2]
        for n in keep:
            opi = n.get("opinion", "")
            title = n.get("title", "")[:80]
            url = n.get("url", "")
            link = f"[{title}]({url})" if url else title
            lines.append(f"  - 隔夜：{link} — {opi}")
        if not keep and not news:
            pass  # silent
        elif not keep:
            lines.append("  - 隔夜：无 thesis-relevant 新闻")

        # 评级
        rating = (data.get("ratings") or {}).get(tkr)
        if rating:
            lines.append(f"  - 评级：{rating}")

        # 8-K
        filings = (data.get("filings") or {}).get(tkr) or []
        if filings:
            f0 = filings[0]
            lines.append(f"  - 8-K: {f0.get('date')} {f0.get('summary', '')[:80]}")

        return lines

    # Portfolio
    if pos_signals:
        L.append(f"### Portfolio ({len(pos_signals)} 只)")
        L.append("")
        for tkr, sig in sorted(pos_signals.items(), key=lambda kv: -float(kv[1].get("market_val") or 0)):
            L.extend(render_entry(tkr, sig, "持仓"))
        L.append("")

    # Watchlist
    if wl_signals:
        L.append(f"### Watchlist ({len(wl_signals)} 只)")
        L.append("")
        for tkr, sig in wl_signals.items():
            L.extend(render_entry(tkr, sig, "关注"))
        L.append("")

    if not pos_signals and not wl_signals:
        L.append("_无持仓且 watchlist 为空_")
        L.append("")

    return "\n".join(L)


# ---------------------------------------------------------------------------
# Part 2 — 持仓盈亏与 Action
# ---------------------------------------------------------------------------

def render_part2(data: dict, position_signals: dict) -> str:
    L = ["## Part 2 — 持仓盈亏与 Action", ""]

    if data.get("portfolio_unavailable"):
        L.append(f"{E_ERROR} 持仓数据不可用 — OpenD 未启动。请启动 moomoo OpenD GUI 并登录后重跑。")
        L.append("")
        return "\n".join(L)

    if not position_signals:
        L.append("_当前无持仓_")
        L.append("")
        return "\n".join(L)

    # Card layout per ticker — readable on mobile (no wrap-around).
    # Markdown table abandoned because:
    #  - Telegram <pre> font wraps at ~32 chars on iPhone, breaking 9-column tables
    #  - PC markdown viewers render multi-line bullets cleanly too
    for tkr, sig in sorted(position_signals.items(), key=lambda kv: -float(kv[1].get("market_val") or 0)):
        p = sig["position"]
        emoji = STATUS_TO_EMOJI.get(sig["status"], E_NO_MEMO)
        label = STATUS_TO_LABEL.get(sig["status"], "")
        action = ACTION_BY_STATUS.get(sig["status"], "持有")
        qty = p.get("qty") or 0
        avg = p.get("average_cost") or 0
        last = p.get("nominal_price") or (p.get("snapshot") or {}).get("last_price") or 0
        # P&L discipline: ONLY unrealized_pl + pl_ratio_avg_cost
        cum_pl = p.get("unrealized_pl")
        cum_pct = p.get("pl_ratio_avg_cost")
        today = p.get("today_pl_val")
        ccy = p.get("currency", "")

        # Line 1: emoji + ticker + status label
        L.append(f"{emoji} **{tkr}** · {label}")
        # Line 2: position (qty × avg → last)
        L.append(f"   {qty:g} sh @ ${avg:.2f} → ${last:.2f}")
        # Line 3: cumulative + today P&L on one line
        L.append(
            f"   累计 {_fmt_money(cum_pl)} {ccy} ({_fmt_pct(cum_pct)}) · 今日 {_fmt_money(today)}"
        )
        # Line 4: action (only show if non-trivial)
        if action and action != "持有":
            L.append(f"   👉 {action}")
        L.append("")  # blank line between tickers

    # Account summary (forwarded from portfolio-fetch summary)
    s = data.get("summary") or {}
    if s:
        L.append(
            f"**账户**：总资产 HK${_fmt_money(s.get('total_assets_hkd')).lstrip('$')} "
            f"/ 流动性 {s.get('liquid_pct_of_total', 0):.1f}% "
            f"/ Top 5 集中度 {s.get('top5_concentration_total_pct', 0):.1f}%（按总资产）"
        )
        risk = (data.get("funds") or {}).get("hkd", {}).get("risk_status")
        if risk:
            L.append(f"**风险等级**：{risk}")
        L.append("")

    return "\n".join(L)


# ---------------------------------------------------------------------------
# Part 3 — Watchlist 入场扫描
# ---------------------------------------------------------------------------

def render_part3(data: dict, watchlist_signals: dict) -> str:
    L = ["## Part 3 — Watchlist 入场扫描", ""]

    if not watchlist_signals:
        L.append("_watchlist 为空，请编辑 `investment-plugin/references/watchlist.json` 添加关注的股票_")
        L.append("")
        return "\n".join(L)

    shown = 0
    for tkr, sig in watchlist_signals.items():
        memo = sig.get("memo") or {}
        price = sig.get("current_price")
        buy = memo.get("buy_zone")
        if not buy or price is None:
            continue
        # distance to buy_zone high (positive = above zone; ≤0 = inside or below)
        dist_pct = (price - buy[1]) / buy[1] * 100
        emoji = STATUS_TO_EMOJI.get(sig["status"], E_NO_MEMO)
        if sig["status"] in ("in_buy", "below_buy"):
            mid = _midpoint(buy)
            line = (
                f"- **{tkr}** ${price:.2f} {emoji} Buy Zone {_zone_str(buy)} — "
                f"**已进入**，准备挂限价 ${mid:.2f}"
            )
            L.append(line)
            shown += 1
        elif -5 <= dist_pct < 0:
            L.append(f"- **{tkr}** ${price:.2f} Buy Zone {_zone_str(buy)} — 距 -{abs(dist_pct):.1f}%，接近 Buy Zone")
            shown += 1
        else:
            # silent (too far)
            pass

        # nearest catalyst on highlighted entries
        cats = memo.get("catalysts") or []
        if shown and cats and (sig["status"] in ("in_buy", "below_buy") or -5 <= dist_pct < 0):
            c = cats[0]
            L.append(f"  - 催化剂：{c['date']} {c['event']}")

    if shown == 0:
        L.append("_所有 watchlist 标的距 Buy Zone > 5%，静默_")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

def build_signals(data: dict) -> tuple[dict, dict]:
    """Return (position_signals, watchlist_signals)."""
    positions = data.get("positions") or []
    watchlist = data.get("watchlist") or []
    memos = data.get("memos") or {}
    focus = data.get("focus")

    pos_idx = _index_positions(positions)
    watching_tickers = {w["ticker"] for w in watchlist}

    pos_signals = {}
    for tkr, p in pos_idx.items():
        if focus and tkr != focus:
            continue
        memo = memos.get(tkr)
        price = (p.get("snapshot") or {}).get("last_price") or p.get("nominal_price")
        status = zone_status(price, memo)
        pos_signals[tkr] = {
            "position": p,
            "memo": memo,
            "status": status,
            "market_val": p.get("market_val") or 0,
            "name": p.get("stock_name") or "",
        }

    wl_signals = {}
    for w in watchlist:
        tkr = w["ticker"]
        if focus and tkr != focus:
            continue
        if tkr in pos_idx:
            continue  # already in portfolio — handled by pos_signals
        memo = memos.get(tkr)
        price = w.get("current_price")
        status = zone_status(price, memo)
        wl_signals[tkr] = {
            "memo": memo,
            "status": status,
            "current_price": price,
            "name": w.get("name") or "",
        }

    return pos_signals, wl_signals


def render(data: dict) -> str:
    pos_signals, wl_signals = build_signals(data)
    top_call = elect_top_call(data, pos_signals, wl_signals)

    date_s = data.get("date") or date.today().isoformat()
    fetched = data.get("fetched_at") or datetime.now().isoformat(timespec="seconds")

    L = []
    L.append(f"# {date_s} Morning Update")
    L.append("")
    if data.get("portfolio_unavailable"):
        L.append(f"{E_ERROR} **持仓数据不可用** — OpenD 未启动，Part 2 跳过")
        L.append("")
    L.append(f"## {E_TOP} Top Call")
    L.append(top_call)
    L.append("")
    L.append("---")
    L.append("")
    L.append(render_part1(data, pos_signals, wl_signals))
    L.append("---")
    L.append("")
    L.append(render_part2(data, pos_signals))
    L.append("---")
    L.append("")
    L.append(render_part3(data, wl_signals))
    L.append("---")
    L.append("")
    n_pos = len(pos_signals)
    n_wl = len(wl_signals)
    L.append(f"_生成于 {fetched} · 持仓 {n_pos} / 关注 {n_wl}_")
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
