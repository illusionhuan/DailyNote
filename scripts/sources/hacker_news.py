import logging
from common import make_session, normalize_score

logger = logging.getLogger("trending.hn")

API_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
API_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"


def fetch_hn(limit=15):
    session = make_session()
    articles = []

    try:
        ids = session.get(API_TOP, timeout=10).json()[:50]
    except Exception as e:
        logger.error("HN top stories fetch failed: %s", e)
        return []

    for story_id in ids:
        if len(articles) >= limit:
            break
        try:
            item = session.get(API_ITEM.format(story_id), timeout=5).json()
        except Exception:
            continue
        if not item or item.get("type") != "story" or not item.get("url"):
            continue
        if item.get("score", 0) < 10:
            continue
        articles.append({
            "title": item.get("title", ""),
            "url": item["url"],
            "source": "hacker_news",
            "score": normalize_score("hacker_news", item.get("score", 0)),
            "raw_score": item.get("score", 0),
            "comments": item.get("descendants", 0),
            "author": item.get("by", ""),
            "created_at": "",
            "summary": "",
        })

    articles.sort(key=lambda x: x["raw_score"], reverse=True)
    logger.info("HN: fetched %d articles", len(articles))
    return articles
