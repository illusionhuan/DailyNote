import logging
from common import make_session, normalize_score

logger = logging.getLogger("trending.v2ex")

API_URL = "https://www.v2ex.com/api/topics/hot.json"


def fetch_v2ex(limit=10):
    session = make_session()
    articles = []

    try:
        resp = session.get(API_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error("V2EX fetch failed: %s", e)
        return []

    for topic in data[:limit]:
        replies = topic.get("replies", 0)
        if replies < 5:
            continue
        member = topic.get("member", {})
        articles.append({
            "title": topic.get("title", ""),
            "url": topic.get("url", ""),
            "source": "v2ex",
            "score": normalize_score("v2ex", replies),
            "raw_score": replies,
            "comments": replies,
            "author": member.get("username", ""),
            "created_at": "",
            "summary": "",
        })

    articles.sort(key=lambda x: x["raw_score"], reverse=True)
    logger.info("V2EX: fetched %d topics", len(articles))
    return articles
