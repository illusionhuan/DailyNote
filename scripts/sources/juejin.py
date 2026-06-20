import logging
from common import make_session, normalize_score

logger = logging.getLogger("trending.juejin")

API_URL = "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed"


def fetch_juejin(limit=15):
    session = make_session()
    session.headers.update({
        "Content-Type": "application/json",
        "Referer": "https://juejin.cn/",
    })
    articles = []

    try:
        resp = session.post(API_URL, json={
            "id_type": 0,
            "sort_type": 0,
            "cursor": "0",
            "limit": limit * 2,
        }, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error("Juejin fetch failed: %s", e)
        return []

    for item in (data.get("data") or []):
        if len(articles) >= limit:
            break
        ii = item.get("item_info", {})
        info = ii.get("article_info", {})
        author = ii.get("author_user_info", {})
        article_id = info.get("article_id", "")
        if not article_id:
            continue
        views = int(info.get("view_count") or 0)
        if views < 5000:
            continue
        articles.append({
            "title": info.get("title", ""),
            "url": f"https://juejin.cn/post/{article_id}",
            "source": "juejin",
            "score": normalize_score("juejin", views),
            "raw_score": views,
            "comments": int(info.get("comment_count") or 0),
            "author": author.get("user_name", ""),
            "created_at": "",
            "summary": info.get("brief_content", ""),
        })

    articles.sort(key=lambda x: x["raw_score"], reverse=True)
    logger.info("Juejin: fetched %d articles", len(articles))
    return articles
