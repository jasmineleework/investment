#!/usr/bin/env python3
"""
FRED (Federal Reserve Economic Data) Fetcher

Usage: python3 fred_fetch.py [SERIES_ID] [FRED_API_KEY]
Defaults: SERIES_ID=DGS10 (10-Year US Treasury yield)
Output: JSON { "series_id": "...", "date": "...", "value": "..." }

Dependencies: requests
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


def fetch_json_api(series_id: str, api_key: str) -> Optional[dict]:
    """Strategy 1: FRED JSON API (requires API key)."""
    print(f"Fetching {series_id} via FRED JSON API...", file=sys.stderr)
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={api_key}"
        f"&file_type=json&limit=5&sort_order=desc"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        observations = resp.json().get("observations", [])
        for obs in observations:
            if obs["value"] != ".":
                return {"series_id": series_id, "date": obs["date"], "value": obs["value"]}
    except Exception:
        pass
    return None


def fetch_csv(series_id: str) -> Optional[dict]:
    """Strategy 2: FRED CSV endpoint (no API key required)."""
    print(f"Fetching {series_id} via FRED CSV endpoint...", file=sys.stderr)
    date_30d_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={date_30d_ago}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
        if len(lines) < 2:
            return None
        last_line = lines[-1]
        parts = last_line.split(",")
        if len(parts) >= 2 and parts[1] != "." and parts[1]:
            return {"series_id": series_id, "date": parts[0], "value": parts[1]}
    except Exception:
        pass
    return None


def main():
    series_id = sys.argv[1] if len(sys.argv) > 1 else "DGS10"
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("FRED_API_KEY", "")

    result = None

    # Strategy 1: JSON API (if key available)
    if api_key:
        result = fetch_json_api(series_id, api_key)
        if not result:
            print("JSON API failed, falling back to CSV...", file=sys.stderr)

    # Strategy 2: CSV endpoint
    if not result:
        result = fetch_csv(series_id)

    if result:
        print(json.dumps(result))
    else:
        print(f"Error: Could not fetch {series_id} from FRED (both JSON API and CSV failed)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
