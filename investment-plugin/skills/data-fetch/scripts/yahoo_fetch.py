#!/usr/bin/env python3
"""
Yahoo Finance Data Fetcher

Usage: python3 yahoo_fetch.py <TICKER>
Output: JSON to stdout with quote, financials, balanceSheet, cashFlow,
        historicalPrices, analystRatings, errors.

Dependencies: yfinance
"""

import json
import math
import sys
from datetime import datetime, timedelta

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


def fetch_all(symbol: str) -> dict:
    result = {
        "ticker": symbol,
        "fetchDate": datetime.now().strftime("%Y-%m-%d"),
        "quote": None,
        "financials": None,
        "balanceSheet": None,
        "cashFlow": None,
        "historicalPrices": None,
        "analystRatings": None,
        "majorHolders": None,
        "institutionalHolders": None,
        "errors": [],
    }

    t = yf.Ticker(symbol)

    # Quote summary
    try:
        info = t.info
        result["quote"] = {
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "marketCap": info.get("marketCap"),
            "currency": info.get("currency"),
            "exchange": info.get("exchange"),
            "name": info.get("longName") or info.get("shortName"),
            "pe": info.get("trailingPE"),
            "forwardPe": info.get("forwardPE"),
            "pb": info.get("priceToBook"),
            "ps": info.get("priceToSalesTrailing12Months"),
            "evToEbitda": info.get("enterpriseToEbitda"),
            "evToRevenue": info.get("enterpriseToRevenue"),
            "dividendYield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "avgVolume": info.get("averageVolume"),
            "sharesOutstanding": info.get("sharesOutstanding"),
            "floatShares": info.get("floatShares"),
            "shortRatio": info.get("shortRatio"),
            "targetMeanPrice": info.get("targetMeanPrice"),
            "targetHighPrice": info.get("targetHighPrice"),
            "targetLowPrice": info.get("targetLowPrice"),
            "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
            "recommendationKey": info.get("recommendationKey"),
            "grossMargin": info.get("grossMargins"),
            "operatingMargin": info.get("operatingMargins"),
            "profitMargin": info.get("profitMargins"),
            "returnOnEquity": info.get("returnOnEquity"),
            "returnOnAssets": info.get("returnOnAssets"),
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "totalDebt": info.get("totalDebt"),
            "totalCash": info.get("totalCash"),
            "debtToEquity": info.get("debtToEquity"),
            "currentRatio": info.get("currentRatio"),
            "freeCashflow": info.get("freeCashflow"),
            "operatingCashflow": info.get("operatingCashflow"),
        }
    except Exception as e:
        result["errors"].append(f"quote: {e}")

    # Income statement (annual + quarterly)
    try:
        annual = t.financials
        quarterly = t.quarterly_financials
        result["financials"] = {
            "annual": _df_to_records(annual),
            "quarterly": _df_to_records(quarterly),
        }
    except Exception as e:
        result["errors"].append(f"financials: {e}")

    # Balance sheet
    try:
        annual = t.balance_sheet
        result["balanceSheet"] = {
            "annual": _df_to_records(annual),
        }
    except Exception as e:
        result["errors"].append(f"balanceSheet: {e}")

    # Cash flow
    try:
        annual = t.cashflow
        result["cashFlow"] = {
            "annual": _df_to_records(annual),
        }
    except Exception as e:
        result["errors"].append(f"cashFlow: {e}")

    # Historical prices (2 years, weekly)
    try:
        two_years_ago = datetime.now() - timedelta(days=730)
        hist = t.history(start=two_years_ago.strftime("%Y-%m-%d"), interval="1wk")
        result["historicalPrices"] = [
            {
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 4),
                "high": round(row["High"], 4),
                "low": round(row["Low"], 4),
                "close": round(row["Close"], 4),
                "volume": int(row["Volume"]),
            }
            for idx, row in hist.iterrows()
        ]
    except Exception as e:
        result["errors"].append(f"historicalPrices: {e}")

    # Analyst ratings
    try:
        rec = t.recommendations
        if rec is not None and not rec.empty:
            result["analystRatings"] = {
                "trend": _df_to_records(rec.tail(10)),
            }
        else:
            result["analystRatings"] = {"trend": []}
    except Exception as e:
        result["errors"].append(f"analystRatings: {e}")

    # Major holders (institutional/insider ownership %)
    try:
        major = t.major_holders
        result["majorHolders"] = _df_to_records(major) if major is not None and not major.empty else []
    except Exception as e:
        result["errors"].append(f"majorHolders: {e}")

    # Top institutional holders
    try:
        inst = t.institutional_holders
        result["institutionalHolders"] = _df_to_records(inst.head(10)) if inst is not None and not inst.empty else []
    except Exception as e:
        result["errors"].append(f"institutionalHolders: {e}")

    return result


def _df_to_records(df) -> list:
    """Convert a pandas DataFrame to a list of dicts with string keys."""
    if df is None or df.empty:
        return []
    # Transpose if columns are dates (yfinance convention)
    if hasattr(df.columns[0], "strftime"):
        df = df.T
    records = []
    for idx, row in df.iterrows():
        rec = {"date": str(idx)}
        for col in df.columns:
            val = row[col]
            # Convert numpy types to Python native
            if hasattr(val, "item"):
                val = val.item()
            # NaN → None for valid JSON
            if isinstance(val, float) and math.isnan(val):
                val = None
            rec[str(col)] = val
        records.append(rec)
    return records


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 yahoo_fetch.py <TICKER>", file=sys.stderr)
        sys.exit(1)

    symbol = sys.argv[1].upper()
    data = fetch_all(symbol)
    print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
