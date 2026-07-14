#!/usr/bin/env python3
"""
check_urls.py — guard against hand-typed / truncated article URLs.

Every URL in must_read / worth_reading / news_curated of the render input
MUST exist verbatim in the news_fetch candidates JSON (they were scraped —
never retype them). discovery.source_articles is exempt (may come from
WebSearch).

Usage:
  python3 check_urls.py /tmp/morning_input.json /tmp/news_candidates.json
Exit 1 + offending URLs on stderr if any URL is not found verbatim.
"""
import json
import sys
from urllib.parse import urlsplit, urlunsplit


def _norm(url: str) -> str:
    """Compare on scheme+host+path — tracking query params may legitimately
    be dropped, but a truncated/hand-typed path slug must fail."""
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path.rstrip("/"), "", ""))


def collect_candidate_urls(cand: dict) -> set:
    urls = set()
    for it in cand.get("must_push", []) + cand.get("macro", []):
        urls.add(it.get("url", ""))
    for items in cand.get("matched", {}).values():
        for it in items:
            urls.add(it.get("url", ""))
    for cl in cand.get("unmatched_hot", []):
        for it in cl.get("items", []):
            urls.add(it.get("url", ""))
    urls.discard("")
    return {_norm(u) for u in urls}


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    cand = json.load(open(sys.argv[2], encoding="utf-8"))
    pool = collect_candidate_urls(cand)

    bad = []
    for section in ("must_read", "worth_reading", "news_curated"):
        for it in data.get(section) or []:
            u = it.get("url", "")
            if u and _norm(u) not in pool:
                bad.append((section, u))
    if bad:
        print("URL INTEGRITY FAIL — 以下 URL 不在 news_candidates 中（疑似手敲/截断）：", file=sys.stderr)
        for sec, u in bad:
            print(f"  [{sec}] {u}", file=sys.stderr)
        return 1
    print(f"url check OK ({len(pool)} candidate urls)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
