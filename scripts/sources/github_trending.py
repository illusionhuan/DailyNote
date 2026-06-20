import re
import logging
from bs4 import BeautifulSoup
from common import make_session, normalize_score

logger = logging.getLogger("trending.github")

TRENDING_URL = "https://github.com/trending"


def fetch_github(limit=15):
    session = make_session()
    articles = []

    try:
        resp = session.get(TRENDING_URL, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error("GitHub Trending fetch failed: %s", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("article.Box-row")

    for row in rows[:limit]:
        try:
            links = row.select("h2 a")
            if not links:
                continue
            href = links[0].get("href", "").strip()
            parts = [p.strip() for p in href.strip("/").split("/") if p.strip()]
            if len(parts) < 2:
                continue
            repo_name = f"{parts[-2]}/{parts[-1]}"
            repo_url = f"https://github.com{href}"

            desc_el = row.select_one("p")
            description = desc_el.get_text(strip=True) if desc_el else ""

            lang_el = row.select_one("[itemprop='programmingLanguage']")
            language = lang_el.get_text(strip=True) if lang_el else ""

            star_text = row.select_one("a[href$='/stargazers']")
            stars = int(star_text.get_text(strip=True).replace(",", "")) if star_text else 0

            fork_text = row.select_one("a[href$='/forks']")
            forks = int(fork_text.get_text(strip=True).replace(",", "")) if fork_text else 0

            today_text = row.select_one("span.d-inline-block.float-sm-right")
            today = 0
            if today_text:
                m = re.search(r"([\d,]+)", today_text.get_text())
                if m:
                    today = int(m.group(1).replace(",", ""))

            score = stars + today * 10
            articles.append({
                "title": repo_name,
                "url": repo_url,
                "source": "github",
                "score": normalize_score("github", score),
                "raw_score": score,
                "comments": forks,
                "author": parts[-2],
                "created_at": "",
                "summary": description,
            })
        except Exception as e:
            logger.debug("GitHub row parse error: %s", e)
            continue

    articles.sort(key=lambda x: x["raw_score"], reverse=True)
    logger.info("GitHub: fetched %d repos", len(articles))
    return articles
