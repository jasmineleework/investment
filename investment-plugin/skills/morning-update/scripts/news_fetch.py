#!/usr/bin/env python3
"""
news_fetch.py — RSS aggregation for morning-update. stdlib only (py3.9+).

Fetches feeds from references/feeds.json, filters by watchlist tickers /
company names / concept keywords (references/../..../references/concepts.json),
dedupes, and emits four buckets as JSON to stdout:

  must_push     — items from must_push feeds (e.g. Citrini). NO keyword filter,
                  wider time window (--must-push-hours, default 48).
  matched       — {ticker_or_concept_id: [items]} within --hours.
  macro         — items hitting macro_keywords (feeds.json).
  unmatched_hot — title clusters appearing across >=2 sources but matching
                  nothing above; Discovery fodder.

Usage:
  python3 news_fetch.py --tickers AVGO,COHR,CLS --hours 24 --json

Per-feed fetch stats go to stderr. A dead feed never blocks the run.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_REFS = SCRIPT_DIR.parent / "references"
REPO_ROOT = Path(__file__).resolve().parents[4]
PLUGIN_REFS = REPO_ROOT / "investment-plugin" / "references"

# Yahoo 的 RSS 端点会对长 Chrome UA 返回 429；短 UA + Accept 实测通过
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
FETCH_TIMEOUT = 10
SUMMARY_MAX = 300
TITLE_SIM_THRESHOLD = 0.85

ATOM_NS = "{http://www.w3.org/2005/Atom}"
TAG_RE = re.compile(r"<[^>]+>")


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_json(path: Path, required: bool = True):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if required:
            print(f"FATAL: missing config {path}", file=sys.stderr)
            sys.exit(1)
        return None
    except json.JSONDecodeError as e:
        print(f"FATAL: bad JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def load_watchlist_names() -> dict:
    """ticker -> company name, from watchlist.json (optional)."""
    data = load_json(PLUGIN_REFS / "watchlist.json", required=False)
    if not data:
        return {}
    return {
        w["ticker"]: w.get("name", "")
        for w in data.get("watchlist", [])
        if w.get("ticker")
    }


# ---------------------------------------------------------------------------
# Fetch + parse
# ---------------------------------------------------------------------------

def fetch_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 429:  # rate limited — one retry after a pause
            time.sleep(3)
            with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
                return resp.read()
        raise


def fetch_group(group: list) -> list:
    """Fetch a list of (feed, url, forced) sequentially (same host —
    parallel hits trigger 429 on Yahoo). Returns [(feed, url, forced, result_or_exc)]."""
    out = []
    for i, (feed, url, forced) in enumerate(group):
        if i:
            time.sleep(0.5)
        try:
            out.append((feed, url, forced, fetch_feed(url)))
        except Exception as e:  # noqa: BLE001 — one dead URL must not kill the group
            out.append((feed, url, forced, e))
    return out


def _text(el) -> str:
    return html.unescape((el.text or "").strip()) if el is not None else ""


def _clean_summary(raw: str) -> str:
    s = TAG_RE.sub(" ", raw)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:SUMMARY_MAX]


def _parse_date(s: str):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)  # RFC 822 (RSS)
    except (ValueError, TypeError):
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))  # ISO (Atom)
    except ValueError:
        return None


def parse_items(xml_bytes: bytes, source_name: str) -> list:
    root = ET.fromstring(xml_bytes)
    items = []
    # RSS 2.0
    for it in root.iter("item"):
        link_el = it.find("link")
        pub = _text(it.find("pubDate")) or _text(it.find("{http://purl.org/dc/elements/1.1/}date"))
        items.append({
            "title": _text(it.find("title")),
            "url": _text(link_el),
            "published": pub,
            "summary": _clean_summary(_text(it.find("description"))),
            "source": source_name,
        })
    # Atom
    if not items:
        for it in root.iter(f"{ATOM_NS}entry"):
            link = ""
            for l in it.findall(f"{ATOM_NS}link"):
                if l.get("rel") in (None, "alternate"):
                    link = l.get("href", "")
                    break
            items.append({
                "title": _text(it.find(f"{ATOM_NS}title")),
                "url": link,
                "published": _text(it.find(f"{ATOM_NS}published")) or _text(it.find(f"{ATOM_NS}updated")),
                "summary": _clean_summary(_text(it.find(f"{ATOM_NS}summary")) or _text(it.find(f"{ATOM_NS}content"))),
                "source": source_name,
            })
    return [i for i in items if i["title"]]


# ---------------------------------------------------------------------------
# Filtering / matching
# ---------------------------------------------------------------------------

def norm_url(url: str) -> str:
    if not url:
        return ""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def build_matchers(tickers: list, names: dict, concepts: list):
    """Return list of (key, compiled_regex)."""
    matchers = []
    for t in tickers:
        pats = [rf"\b{re.escape(t)}\b"]  # ticker, case-sensitive
        matchers.append((t, re.compile("|".join(pats))))
        name = names.get(t)
        if name:
            matchers.append((t, re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)))
    for c in concepts:
        kws = [rf"\b{re.escape(k)}\b" for k in c.get("keywords", [])]
        if kws:
            matchers.append((c["id"], re.compile("|".join(kws), re.IGNORECASE)))
    return matchers


def match_item(item: dict, matchers: list, forced_ticker=None) -> list:
    """Return list of matched keys (tickers / concept ids)."""
    keys = []
    if forced_ticker:
        keys.append(forced_ticker)
    text = f"{item['title']} {item['summary']}"
    for key, rx in matchers:
        if key not in keys and rx.search(text):
            keys.append(key)
    return keys


def _norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def dedupe(items: list) -> list:
    """URL exact + title-similarity dedupe; keep higher feed weight."""
    by_url = {}
    for it in items:
        u = norm_url(it["url"])
        key = u or it["title"]
        if key not in by_url or it["_weight"] > by_url[key]["_weight"]:
            by_url[key] = it
    result = []
    for it in sorted(by_url.values(), key=lambda x: -x["_weight"]):
        nt = _norm_title(it["title"])
        dup = any(
            SequenceMatcher(None, nt, _norm_title(kept["title"])).ratio() > TITLE_SIM_THRESHOLD
            for kept in result
        )
        if not dup:
            result.append(it)
    return result


def cluster_hot(items: list) -> list:
    """Group unmatched items whose titles are similar; keep clusters seen
    across >=2 distinct sources."""
    clusters = []
    for it in items:
        nt = _norm_title(it["title"])
        placed = False
        for cl in clusters:
            if SequenceMatcher(None, nt, cl["_norm"]).ratio() > 0.6:
                cl["items"].append(it)
                placed = True
                break
        if not placed:
            clusters.append({"_norm": nt, "items": [it]})
    hot, singles = [], []
    for cl in clusters:
        sources = {i["source"] for i in cl["items"]}
        entry = {
            "headline": cl["items"][0]["title"],
            "sources": sorted(sources),
            "items": [_public(i) for i in cl["items"]],
            "_w": max(i.get("_weight", 5) for i in cl["items"]),
        }
        (hot if len(sources) >= 2 else singles).append(entry)
    hot.sort(key=lambda c: -len(c["sources"]))
    # Cross-source clusters are rare in practice — top up with high-weight
    # singletons so Discovery always has fodder (cap 12 entries total).
    singles.sort(key=lambda c: -c["_w"])
    for s in singles:
        if len(hot) >= 12:
            break
        hot.append(s)
    for h in hot:
        h.pop("_w", None)
    return hot


def _public(item: dict) -> dict:
    return {k: v for k, v in item.items() if not k.startswith("_")}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="RSS aggregation for morning-update")
    ap.add_argument("--tickers", default="", help="Comma-separated tickers")
    ap.add_argument("--hours", type=int, default=24, help="Freshness window for regular items")
    ap.add_argument("--must-push-hours", type=int, default=48, help="Freshness window for must_push feeds")
    ap.add_argument("--json", action="store_true", help="(default) JSON to stdout")
    args = ap.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]

    cfg = load_json(SKILL_REFS / "feeds.json")
    concepts_cfg = load_json(PLUGIN_REFS / "concepts.json", required=False) or {}
    concepts = concepts_cfg.get("concepts", [])
    names = load_watchlist_names()

    # Expand fetch jobs
    jobs = []  # (feed_dict, url, forced_ticker)
    for feed in cfg.get("feeds", []):
        if not feed.get("enabled", True):
            continue
        if feed.get("category") == "ticker_template":
            for t in tickers:
                jobs.append((feed, feed["url_template"].format(ticker=t), t))
        else:
            jobs.append((feed, feed["url"], None))

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=args.hours)
    cutoff_must = now - timedelta(hours=args.must_push_hours)

    # Group jobs by feed id: per-ticker URLs of the same feed hit one host,
    # so they run sequentially inside a group; groups run in parallel.
    groups = {}
    for feed, url, forced in jobs:
        groups.setdefault(feed["id"], []).append((feed, url, forced))

    all_items = []
    stats = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(fetch_group, g) for g in groups.values()]
        for fut in as_completed(futs):
            for feed, url, forced, result in fut.result():
                fid = feed["id"] + (f":{forced}" if forced else "")
                if isinstance(result, Exception):
                    stats[fid] = f"FAIL {type(result).__name__}"
                    continue
                try:
                    items = parse_items(result, feed.get("name", feed["id"]))
                except ET.ParseError as e:
                    stats[fid] = f"FAIL {type(e).__name__}"
                    continue
                for it in items:
                    it["_feed"] = feed
                    it["_weight"] = feed.get("weight", 5)
                    it["_forced"] = forced
                    it["_dt"] = _parse_date(it["published"])
                all_items.extend(items)
                stats[fid] = f"ok {len(items)}"

    for fid in sorted(stats):
        print(f"[feed] {fid}: {stats[fid]}", file=sys.stderr)

    # Freshness filter (must_push feeds get the wider window; undated items
    # are kept only for must_push feeds)
    fresh = []
    for it in all_items:
        is_must = it["_feed"].get("must_push", False)
        dt = it["_dt"]
        if dt is None:
            if is_must:
                fresh.append(it)
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if dt >= (cutoff_must if is_must else cutoff):
            fresh.append(it)

    fresh = dedupe(fresh)

    matchers = build_matchers(tickers, names, concepts)
    macro_kws = cfg.get("macro_keywords", [])
    macro_rx = re.compile("|".join(rf"\b{re.escape(k)}\b" for k in macro_kws), re.IGNORECASE) if macro_kws else None

    must_push, matched, macro, unmatched = [], {}, [], []
    for it in fresh:
        if it["_feed"].get("must_push", False):
            must_push.append(_public(it))
            continue
        keys = match_item(it, matchers, forced_ticker=it["_forced"])
        # ticker_template feeds force-assign their ticker, but still require a
        # real content match OR being the only assignment (Yahoo per-ticker
        # feeds are already ticker-scoped, so forced counts as a match)
        if keys:
            for k in keys:
                matched.setdefault(k, []).append(_public(it))
        elif macro_rx and macro_rx.search(f"{it['title']} {it['summary']}"):
            macro.append(_public(it))
        else:
            unmatched.append(it)

    out = {
        "generated_at": now.isoformat(timespec="seconds"),
        "params": {"tickers": tickers, "hours": args.hours, "must_push_hours": args.must_push_hours},
        "stats": {
            "feeds": stats,
            "scanned": len(all_items),
            "fresh_after_dedupe": len(fresh),
            "must_push": len(must_push),
            "matched": sum(len(v) for v in matched.values()),
            "macro": len(macro),
            "unmatched": len(unmatched),
        },
        "must_push": must_push,
        "matched": matched,
        "macro": macro,
        "unmatched_hot": cluster_hot(unmatched),
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
