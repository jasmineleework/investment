#!/usr/bin/env python3
"""
portfolio-fetch: pull moomoo SG real portfolio (positions + funds + quote snapshot)
and emit markdown report (default) or JSON.

Field discipline — aligns with moomoo App (see moomoo-skills FIELD_MAPPING.md):
  P&L:        unrealized_pl + pl_ratio_avg_cost  (avg cost basis)
  FORBIDDEN:  cost_price / diluted_cost / pl_val / pl_ratio  (diluted basis)
  Aggregation: accinfo_query(currency=...) per currency; do not sum positions across currencies

Read-only. Never calls unlock_trade or any order/cancel API.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from moomoo import (
    OpenQuoteContext,
    OpenSecTradeContext,
    SecurityFirm,
    TrdMarket,
    TrdEnv,
    RET_OK,
)

OPEND_HOST = os.getenv("FUTU_OPEND_HOST", "127.0.0.1")
OPEND_PORT = int(os.getenv("FUTU_OPEND_PORT", "11111"))
DEFAULT_FIRM = SecurityFirm.FUTUSG
SNAPSHOT_BATCH = 400


def _to_native(v):
    if v is None:
        return None
    if hasattr(v, "item"):
        try:
            return v.item()
        except (ValueError, TypeError):
            pass
    return v


def _df_to_records(df):
    if df is None or not hasattr(df, "iterrows") or len(df) == 0:
        return []
    out = []
    for _, row in df.iterrows():
        out.append({k: _to_native(row[k]) for k in df.columns})
    return out


def resolve_account(trd_ctx) -> dict:
    env_acc_id = os.getenv("MOOMOO_PORTFOLIO_ACC_ID")
    ret, df = trd_ctx.get_acc_list()
    if ret != RET_OK:
        raise RuntimeError(f"get_acc_list failed: {df}")
    accs = _df_to_records(df)

    if env_acc_id:
        target = next((a for a in accs if str(a.get("acc_id")) == env_acc_id), None)
        if not target:
            raise RuntimeError(f"MOOMOO_PORTFOLIO_ACC_ID={env_acc_id} not in {len(accs)} accounts")
        return target

    real = [a for a in accs if str(a.get("trd_env")) == "REAL" and str(a.get("acc_role")) != "MASTER"]
    if not real:
        raise RuntimeError("No REAL non-MASTER account found. Confirm OpenD is logged into the SG live account.")
    return real[0]


def _nullify_na(rec: dict) -> dict:
    """Replace string 'N/A' with None so downstream formatting treats it as empty."""
    return {k: (None if v == "N/A" else v) for k, v in rec.items()}


def _safe_num(v):
    if v is None or v == "N/A":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def fetch_funds(trd_ctx, acc_id: int, currency: str) -> dict:
    ret, df = trd_ctx.accinfo_query(trd_env=TrdEnv.REAL, acc_id=acc_id, currency=currency)
    if ret != RET_OK:
        return {"_error": str(df)}
    recs = _df_to_records(df)
    if not recs:
        return {}
    rec = _nullify_na(recs[0])
    # SG / non-US accounts return 'N/A' for available_funds; per FIELD_MAPPING.md
    # fall back to total_assets - initial_margin.
    if rec.get("available_funds") is None:
        ta, im = _safe_num(rec.get("total_assets")), _safe_num(rec.get("initial_margin"))
        if ta is not None:
            rec["available_funds"] = ta - im if (im and im > 0) else ta
    return rec


def fetch_positions(trd_ctx, acc_id: int) -> list:
    ret, df = trd_ctx.position_list_query(trd_env=TrdEnv.REAL, acc_id=acc_id)
    if ret != RET_OK:
        raise RuntimeError(f"position_list_query failed: {df}")
    return _df_to_records(df)


def fetch_snapshots(quote_ctx, codes: list) -> dict:
    out = {}
    for i in range(0, len(codes), SNAPSHOT_BATCH):
        batch = codes[i:i + SNAPSHOT_BATCH]
        ret, df = quote_ctx.get_market_snapshot(batch)
        if ret != RET_OK:
            print(f"[WARN] snapshot batch {i//SNAPSHOT_BATCH} failed: {df}", file=sys.stderr)
            continue
        for rec in _df_to_records(df):
            out[rec["code"]] = rec
    return out


# Whitelist: only App-aligned fields exit this skill
POSITION_KEEP = [
    "code", "stock_name", "position_market", "currency",
    "qty", "can_sell_qty",
    "average_cost", "nominal_price", "market_val",
    "unrealized_pl", "pl_ratio_avg_cost",
    "realized_pl", "today_pl_val",
    "position_side",
]

SNAPSHOT_KEEP = [
    "last_price", "prev_close_price", "open_price", "high_price", "low_price",
    "pe_ratio", "pe_ttm_ratio", "pb_ratio",
    "earning_per_share", "net_asset_per_share",
    "dividend_ttm", "dividend_ratio_ttm",
    "highest52weeks_price", "lowest52weeks_price",
    "total_market_val", "circular_market_val", "issued_shares",
    "update_time",
]

FUNDS_KEEP = [
    "total_assets", "market_val", "long_mv", "short_mv",
    "cash", "us_cash", "ca_cash",
    "avl_withdrawal_cash", "frozen_cash",
    "available_funds", "power",
    "initial_margin", "maintenance_margin",
    "risk_status",
]


def build_portfolio(acc_id: int) -> dict:
    trd = OpenSecTradeContext(
        host=OPEND_HOST, port=OPEND_PORT,
        filter_trdmarket=TrdMarket.NONE,
        security_firm=DEFAULT_FIRM,
    )
    q = OpenQuoteContext(host=OPEND_HOST, port=OPEND_PORT)
    try:
        funds_hkd_raw = fetch_funds(trd, acc_id, "HKD")
        funds_usd_raw = fetch_funds(trd, acc_id, "USD")
        positions_raw = fetch_positions(trd, acc_id)

        codes = sorted({p["code"] for p in positions_raw if p.get("code")})
        snapshots = fetch_snapshots(q, codes) if codes else {}

        positions = []
        for p in positions_raw:
            kept = {f: p.get(f) for f in POSITION_KEEP}
            snap_raw = snapshots.get(p.get("code"), {})
            kept["snapshot"] = {f: snap_raw.get(f) for f in SNAPSHOT_KEEP}
            positions.append(kept)

        # account-level total (USD basis) from accinfo_query — DO NOT sum positions
        total_usd = funds_usd_raw.get("market_val")
        total_hkd = funds_hkd_raw.get("market_val")

        # concentration: weight by position market_val within its own currency, then aggregate
        # simpler & honest: weight by market_val converted via accinfo HKD-vs-USD ratio
        weights = []
        if positions and total_hkd:
            # use HKD basis for weights (account base currency)
            # convert each position's market_val to HKD using accinfo ratio
            if funds_usd_raw.get("market_val") and funds_hkd_raw.get("market_val"):
                # implicit USD->HKD multiplier (not exact for mixed positions, but App uses same)
                pass
            # For weight, since positions in different currencies, we approximate
            # using account-level HKD market_val total and per-position market_val_in_HKD
            # which is unavailable here. Fall back to ratio of position market_val to
            # *sum of positions in same currency*, then weighted by currency share of total.
            # Simpler & exact: do per-currency weighting + global weighting using funds.
            # For now: report top-5 by raw market_val * fx, where fx normalized by USD ratio
            usd_to_hkd = None
            if funds_usd_raw.get("market_val") and funds_hkd_raw.get("market_val") and funds_usd_raw["market_val"] > 0:
                usd_to_hkd = funds_hkd_raw["market_val"] / funds_usd_raw["market_val"]
            for p in positions:
                mv = p.get("market_val") or 0
                cur = (p.get("currency") or "").upper()
                if cur == "USD" and usd_to_hkd:
                    mv_hkd = mv * usd_to_hkd
                elif cur == "HKD":
                    mv_hkd = mv
                else:
                    mv_hkd = mv  # fallback; mark unknown
                weights.append({"code": p["code"], "mv_hkd": mv_hkd, "currency": cur})
            sum_hkd = sum(w["mv_hkd"] for w in weights)
            for w in weights:
                w["weight_pct"] = (w["mv_hkd"] / sum_hkd * 100) if sum_hkd else 0
            weights.sort(key=lambda x: x["mv_hkd"], reverse=True)

        top5_pct = sum(w["weight_pct"] for w in weights[:5])
        hhi = sum(w["weight_pct"] ** 2 for w in weights)

        return {
            "acc_id": acc_id,
            "security_firm": "FUTUSG",
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "funds": {
                "hkd": {f: funds_hkd_raw.get(f) for f in FUNDS_KEEP},
                "usd": {f: funds_usd_raw.get(f) for f in FUNDS_KEEP},
            },
            "positions": positions,
            "weights": weights,
            "summary": {
                "n_positions": len(positions),
                "total_market_val_hkd": total_hkd,
                "total_market_val_usd": total_usd,
                "top5_concentration_pct": round(top5_pct, 2),
                "hhi": round(hhi, 0),
            },
        }
    finally:
        trd.close()
        q.close()


def _fmt(v, width=None, prec=2):
    if v is None or v == "":
        return "—"
    try:
        fv = float(v)
    except (ValueError, TypeError):
        return str(v)
    if abs(fv) >= 1e9:
        s = f"{fv/1e9:.2f}B"
    elif abs(fv) >= 1e6:
        s = f"{fv/1e6:.2f}M"
    elif abs(fv) >= 1e3:
        s = f"{fv:,.{prec}f}"
    else:
        s = f"{fv:.{prec}f}"
    return s


def render_markdown(data: dict) -> str:
    L = []
    fh = data["funds"]["hkd"]
    fu = data["funds"]["usd"]
    summary = data["summary"]
    fetched = data["fetched_at"]

    L.append(f"# Portfolio Snapshot")
    L.append("")
    L.append(f"- **Account**: `{data['acc_id']}` ({data['security_firm']})")
    L.append(f"- **Fetched**: {fetched}")
    L.append(f"- **Positions**: {summary['n_positions']}")
    L.append("")

    L.append("## Account Summary")
    L.append("")
    L.append("| Metric | HKD | USD |")
    L.append("|---|---:|---:|")
    L.append(f"| Total Assets | {_fmt(fh.get('total_assets'))} | {_fmt(fu.get('total_assets'))} |")
    L.append(f"| Securities MV | {_fmt(fh.get('market_val'))} | {_fmt(fu.get('market_val'))} |")
    L.append(f"| Long MV | {_fmt(fh.get('long_mv'))} | {_fmt(fu.get('long_mv'))} |")
    L.append(f"| Cash (base ccy) | {_fmt(fh.get('cash'))} | {_fmt(fu.get('cash'))} |")
    L.append(f"| US Cash | {_fmt(fh.get('us_cash'))} | {_fmt(fu.get('us_cash'))} |")
    L.append(f"| Available Funds | {_fmt(fh.get('available_funds'))} | {_fmt(fu.get('available_funds'))} |")
    L.append(f"| Buying Power | {_fmt(fh.get('power'))} | {_fmt(fu.get('power'))} |")
    L.append(f"| Initial Margin | {_fmt(fh.get('initial_margin'))} | {_fmt(fu.get('initial_margin'))} |")
    L.append(f"| Risk Status | **{fh.get('risk_status') or '—'}** | — |")
    L.append("")

    L.append("## Positions")
    L.append("")
    L.append("| Code | Name | Mkt | Qty | Avg Cost | Last | MV (ccy) | Unreal P&L | P&L % | PE | PE TTM | 52w Range |")
    L.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    positions = sorted(data["positions"], key=lambda p: float(p.get("market_val") or 0), reverse=True)
    for p in positions:
        snap = p.get("snapshot") or {}
        lo = snap.get("lowest52weeks_price")
        hi = snap.get("highest52weeks_price")
        rng = f"{_fmt(lo)} – {_fmt(hi)}" if lo and hi else "—"
        L.append(
            f"| {p.get('code')} | {p.get('stock_name')} | {p.get('position_market')} "
            f"| {p.get('qty')} | {_fmt(p.get('average_cost'))} | {_fmt(p.get('nominal_price'))} "
            f"| {_fmt(p.get('market_val'))} {p.get('currency','')} "
            f"| {_fmt(p.get('unrealized_pl'))} | {_fmt(p.get('pl_ratio_avg_cost'))}% "
            f"| {_fmt(snap.get('pe_ratio'))} | {_fmt(snap.get('pe_ttm_ratio'))} | {rng} |"
        )
    L.append("")

    L.append("## Concentration (HKD-normalized)")
    L.append("")
    L.append(f"- **Top 5 weight**: {summary['top5_concentration_pct']}%")
    L.append(f"- **HHI**: {int(summary['hhi'])} _(>2500 concentrated, <1500 diversified)_")
    L.append("")
    L.append("| Code | Weight |")
    L.append("|---|---:|")
    for w in data["weights"][:10]:
        L.append(f"| {w['code']} | {w['weight_pct']:.1f}% |")
    L.append("")

    # by market
    by_mkt = {}
    for w in data["weights"]:
        m = next((p.get("position_market") for p in positions if p["code"] == w["code"]), "?")
        by_mkt.setdefault(m, 0)
        by_mkt[m] += w["weight_pct"]
    L.append("## Market Exposure")
    L.append("")
    L.append("| Market | Weight |")
    L.append("|---|---:|")
    for m, w in sorted(by_mkt.items(), key=lambda x: -x[1]):
        L.append(f"| {m} | {w:.1f}% |")
    L.append("")

    return "\n".join(L)


def main():
    p = argparse.ArgumentParser(description="moomoo SG portfolio snapshot (read-only)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--json", action="store_true", help="output raw JSON only")
    g.add_argument("--md", action="store_true", help="output markdown only (default)")
    g.add_argument("--both", action="store_true", help="markdown then JSON")
    p.add_argument("--acc-id", type=int, help="override account id")
    args = p.parse_args()

    if args.acc_id:
        acc_id = args.acc_id
    else:
        trd = OpenSecTradeContext(
            host=OPEND_HOST, port=OPEND_PORT,
            filter_trdmarket=TrdMarket.NONE,
            security_firm=DEFAULT_FIRM,
        )
        try:
            acc = resolve_account(trd)
            acc_id = int(acc["acc_id"])
        finally:
            trd.close()

    data = build_portfolio(acc_id)

    if args.json:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2, default=str)
        sys.stdout.write("\n")
    elif args.both:
        sys.stdout.write(render_markdown(data))
        sys.stdout.write("\n\n---\n\n```json\n")
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2, default=str)
        sys.stdout.write("\n```\n")
    else:
        sys.stdout.write(render_markdown(data))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
