import requests
from datetime import datetime, timezone

API_URL = "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed"
LIMIT = 15
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
}


def fetch(session: requests.Session) -> list[dict]:
    """从掘金 recommend_all_feed API 抓取中文技术文章。"""
    payload = {"id_type": 0, "sort_type": 200, "cursor": "0", "limit": LIMIT}
    resp = session.post(API_URL, json=payload, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if data.get("err_no") != 0:
        raise RuntimeError(f"Juejin API error: {data.get('err_msg')}")

    articles = []
    for item in data.get("data", []):
        item_info = item.get("item_info", {})
        info = item_info.get("article_info", {})
        title = info.get("title", "").strip()
        if not title:
            continue
        views = info.get("view_count", 0)
        comments = info.get("comment_count", 0)
        article_id = info.get("article_id", "")
        author = item_info.get("author_user_info", {}).get("user_name", "")
        articles.append({
            "title": title,
            "url": f"https://juejin.cn/post/{article_id}",
            "source": "juejin",
            "score": _normalize(views),
            "raw_score": views,
            "comments": comments,
            "author": author,
            "created_at": "",
            "summary": info.get("brief_content", "")[:200],
        })
    return articles


def _normalize(views: int) -> int:
    """将浏览量映射到 0-1000 分。"""
    import math
    if views <= 0:
        return 0
    return min(1000, int(math.log10(views) * 200))
