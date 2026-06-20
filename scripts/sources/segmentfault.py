import logging
from bs4 import BeautifulSoup
from common import make_session, normalize_score

logger = logging.getLogger("trending.sf")

PAGE_URL = "https://segmentfault.com/articles"
API_URL = "https://segmentfault.com/api/articles"


def fetch_sf(limit=10):
    session = make_session()
    articles = []

    # Try API first
    try:
        resp = session.get(API_URL, params={
            "page": 1,
            "sort": "heat",
            "limit": limit * 2,
        }, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("rows") or []
        if rows:
            for item in rows[:limit]:
                views = int(item.get("hits", 0))
                if views < 100:
                    continue
                articles.append({
                    "title": item.get("title", ""),
                    "url": f"https://segmentfault.com{item.get('url', '')}",
                    "source": "segmentfault",
                    "score": normalize_score("segmentfault", views),
                    "raw_score": views,
                    "comments": int(item.get("comments", 0)),
                    "author": item.get("author", {}).get("name", "") if isinstance(item.get("author"), dict) else "",
                    "created_at": "",
                    "summary": "",
                })
            articles.sort(key=lambda x: x["raw_score"], reverse=True)
            logger.info("SegmentFault (API): fetched %d articles", len(articles))
            return articles
    except Exception:
        pass

    # Fallback: scrape HTML page
    try:
        resp = session.get(PAGE_URL, params={"sort": "heat"}, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error("SegmentFault fetch failed: %s", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    for card in soup.select("div.article__item, div.list-group-item, article")[:limit * 2]:
        if len(articles) >= limit:
            break
        link = card.select_one("h2 a, h3 a, a.article-title, a[href*='/a/']")
        if not link:
            continue
        title = link.get_text(strip=True)
        href = link.get("href", "")
        if not href.startswith("http"):
            href = f"https://segmentfault.com{href}"
        views_el = card.select_one("span.article__views, span.views, .text-muted")
        views = 0
        if views_el:
            import re
            m = re.search(r"(\d[\d,]*)", views_el.get_text())
            if m:
                views = int(m.group(1).replace(",", ""))
        articles.append({
            "title": title,
            "url": href,
            "source": "segmentfault",
            "score": normalize_score("segmentfault", max(views, 1)),
            "raw_score": views,
            "comments": 0,
            "author": "",
            "created_at": "",
            "summary": "",
        })

    articles.sort(key=lambda x: x["raw_score"], reverse=True)
    logger.info("SegmentFault (HTML): fetched %d articles", len(articles))
    return articles
