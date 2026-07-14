#!/usr/bin/env python3
"""
AkShare HK Stock Data Fetcher (EastMoney-sourced)

Usage: python3 akshare_hk_fetch.py <CODE>
       CODE accepts any format: 00700 / 0700.HK / HK.00700 / 700
Output: JSON to stdout with indicators (key financial metrics / DuPont inputs),
        financialReports (three statements, for cross-validating yfinance),
        dividends, bondYields (China & US 10Y for WACC), errors.

Dependencies: akshare
"""

import json
import re
import sys
import time
from datetime import datetime, timedelta

try:
    import akshare as ak
except ImportError:
    print("Error: akshare not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


def normalize_code(raw: str) -> str:
    """Normalize any HK ticker format to the 5-digit string AkShare expects.

    00700 / 0700.HK / HK.00700 / 700 -> 00700
    """
    digits = re.sub(r"\D", "", raw)
    if not digits or len(digits) > 5:
        raise ValueError(f"Cannot parse HK stock code from '{raw}'")
    return digits.zfill(5)


def _retry(fn, attempts=2, delay=2):
    """EastMoney endpoints are occasionally flaky — retry once before failing."""
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 — surface source errors to errors[]
            last = e
            if i < attempts - 1:
                time.sleep(delay)
    raise last


def _json_safe(val):
    """Convert a pandas/numpy cell to a JSON-safe Python value."""
    if val is None or str(val) == "NaT":
        return None
    if hasattr(val, "item"):
        val = val.item()
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, float) and val != val:  # NaN
        return None
    return val


def _df_to_records(df, limit=None) -> list:
    """Convert a pandas DataFrame to a list of JSON-safe dicts."""
    if df is None or df.empty:
        return []
    if limit:
        df = df.head(limit)
    return [
        {str(col): _json_safe(row[col]) for col in df.columns}
        for _, row in df.iterrows()
    ]


def _pivot_statement(df, periods=4) -> dict:
    """Pivot EastMoney long-format statements (one row per line item per period)
    into {report_date: {item_name: amount}} for the most recent N periods."""
    if df is None or df.empty:
        return {}
    out = {}
    dates = sorted(df["REPORT_DATE"].astype(str).unique(), reverse=True)[:periods]
    for date in dates:
        rows = df[df["REPORT_DATE"].astype(str) == date]
        out[date[:10]] = {
            str(r["STD_ITEM_NAME"]): _json_safe(r["AMOUNT"]) for _, r in rows.iterrows()
        }
    return out


def fetch_all(code: str) -> dict:
    result = {
        "ticker": code,
        "tickerCanonical": f"{code.lstrip('0').zfill(4)}.HK",
        "fetchDate": datetime.now().strftime("%Y-%m-%d"),
        "source": "AkShare (EastMoney)",
        "indicators": None,        # 主要财务指标（年度/报告期）— ROE/杜邦/增长/偿债
        "financialReports": None,  # 三表（东财口径，用于交叉验证 yfinance）
        "dividends": None,         # 分红派息历史
        "bondYields": None,        # 中/美 10Y 国债收益率（WACC 无风险利率）
        "errors": [],
    }

    # Key financial indicators (annual)
    try:
        df = _retry(lambda: ak.stock_financial_hk_analysis_indicator_em(symbol=code, indicator="年度"))
        result["indicators"] = _df_to_records(df, limit=6)
    except Exception as e:
        result["errors"].append(f"indicators: {e}")

    # Three statements (annual) — EastMoney reported figures, pivoted to
    # {report_date: {line_item: amount}} for the latest 4 fiscal years
    reports = {}
    for name, indicator in (("balanceSheet", "资产负债表"), ("incomeStatement", "利润表"), ("cashFlow", "现金流量表")):
        try:
            df = _retry(lambda ind=indicator: ak.stock_financial_hk_report_em(stock=code, symbol=ind, indicator="年度"))
            reports[name] = _pivot_statement(df)
        except Exception as e:
            result["errors"].append(f"financialReports.{name}: {e}")
    result["financialReports"] = reports or None

    # Dividend history (most recent 20 records)
    try:
        df = _retry(lambda: ak.stock_hk_fhpx_detail_ths(symbol=code.lstrip("0").zfill(4)))
        if df is not None and not df.empty and "公告日期" in df.columns:
            df = df.sort_values("公告日期", ascending=False)
        result["dividends"] = _df_to_records(df, limit=20)
    except Exception as e:
        result["errors"].append(f"dividends: {e}")

    # China & US 10Y government bond yields (risk-free rate for WACC)
    try:
        start = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        df = _retry(lambda: ak.bond_zh_us_rate(start_date=start))
        if df is not None and not df.empty:
            cn_col = "中国国债收益率10年"
            us_col = "美国国债收益率10年"
            cn = df[["日期", cn_col]].dropna()
            us = df[["日期", us_col]].dropna()
            result["bondYields"] = {
                "china10Y": {
                    "date": str(cn.iloc[-1]["日期"]),
                    "yieldPct": float(cn.iloc[-1][cn_col]),
                } if not cn.empty else None,
                "us10Y": {
                    "date": str(us.iloc[-1]["日期"]),
                    "yieldPct": float(us.iloc[-1][us_col]),
                } if not us.empty else None,
            }
    except Exception as e:
        result["errors"].append(f"bondYields: {e}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 akshare_hk_fetch.py <CODE>  (e.g. 00700 / 0700.HK)", file=sys.stderr)
        sys.exit(1)

    try:
        code = normalize_code(sys.argv[1])
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    data = fetch_all(code)
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
