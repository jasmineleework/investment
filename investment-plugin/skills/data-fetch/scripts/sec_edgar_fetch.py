#!/usr/bin/env python3
"""
SEC EDGAR XBRL Company Facts Fetcher

Usage: python3 sec_edgar_fetch.py <TICKER>
Output: /tmp/<ticker>_sec_facts.json

Dependencies: requests
"""

import json
import sys

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

UA = "InvestmentResearch/1.0 contact@example.com"
HEADERS = {"User-Agent": UA}


def resolve_cik(ticker: str) -> str:
    """Resolve ticker to zero-padded CIK via SEC company tickers JSON."""
    print(f"Looking up CIK for {ticker}...", file=sys.stderr)
    resp = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    for entry in data.values():
        if entry["ticker"] == ticker:
            return str(entry["cik_str"]).zfill(10)
    raise ValueError(f"Could not resolve CIK for {ticker}")


def fetch_xbrl_facts(cik: str, ticker_lower: str) -> str:
    """Download XBRL company facts JSON and save to /tmp."""
    print("Fetching XBRL company facts...", file=sys.stderr)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    output_path = f"/tmp/{ticker_lower}_sec_facts.json"
    with open(output_path, "w") as f:
        json.dump(resp.json(), f, indent=2)

    print(f"Saved to {output_path}", file=sys.stderr)
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 sec_edgar_fetch.py <TICKER>", file=sys.stderr)
        sys.exit(1)

    ticker = sys.argv[1].upper()
    ticker_lower = ticker.lower()

    try:
        cik = resolve_cik(ticker)
        print(f"CIK: {cik}", file=sys.stderr)
        output_path = fetch_xbrl_facts(cik, ticker_lower)
        print(output_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# Key XBRL fields to look for in the JSON:
#   us-gaap:Revenues / us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
#   us-gaap:GrossProfit
#   us-gaap:OperatingIncomeLoss
#   us-gaap:NetIncomeLoss
#   us-gaap:EarningsPerShareDiluted
#   us-gaap:Assets / us-gaap:Liabilities
#   us-gaap:StockholdersEquity
#   us-gaap:LongTermDebt / us-gaap:ShortTermBorrowings
#   us-gaap:CashAndCashEquivalentsAtCarryingValue
#   us-gaap:NetCashProvidedByOperatingActivities
#   us-gaap:PaymentsToAcquirePropertyPlantAndEquipment

if __name__ == "__main__":
    main()
