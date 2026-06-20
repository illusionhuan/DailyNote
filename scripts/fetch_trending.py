#!/usr/bin/env python3
"""
fetch_trending.py — 主入口：从 5 个平台抓取技术热文，合并去重排序后输出 JSON。
用法：python scripts/fetch_trending.py
"""
import os
import sys
import json
import logging
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from sources.hacker_news import fetch_hn
from sources.github_trending import fetch_github
from sources.juejin import fetch_juejin
from sources.v2ex import fetch_v2ex
from sources.segmentfault import fetch_sf

SOURCES = [
    ("HN",         lambda: fetch_hn(limit=15)),
    ("GitHub",     lambda: fetch_github(limit=15)),
    ("Juejin",     lambda: fetch_juejin(limit=15)),
    ("V2EX",       lambda: fetch_v2ex(limit=10)),
    ("SegmentFault", lambda: fetch_sf(limit=10)),
]


def merge(old_articles, new_articles, top_n=50):
    by_url = {}
    for a in old_articles:
        if a.get("url"):
            by_url[a["url"]] = a
    for a in new_articles:
        if not a.get("url"):
            continue
        existing = by_url.get(a["url"])
        if existing is None or a.get("score", 0) > existing.get("score", 0):
            by_url[a["url"]] = a
    return sorted(by_url.values(), key=lambda x: x.get("score", 0), reverse=True)[:top_n]


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("trending")

    output_path = os.path.join("source", "data", "trending.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    old = []
    if os.path.exists(output_path):
        try:
            with open(output_path, encoding="utf-8") as f:
                old = json.load(f).get("articles", [])
        except Exception:
            pass

    new = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(fn): name for name, fn in SOURCES}
        for future in futures:
            name = futures[future]
            try:
                new.extend(future.result())
            except Exception as e:
                logger.error("%s raised: %s", name, e)

    articles = merge(old, new, top_n=50)
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "articles": articles,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info("Done — %d new, %d merged, %d saved", len(new), len(old) + len(new), len(articles))
    print(f"Fetched {len(new)} articles, saved {len(articles)} to {output_path}")


if __name__ == "__main__":
    main()
