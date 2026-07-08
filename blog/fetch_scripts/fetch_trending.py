"""抓取中文技术热文并输出到 source/data/trending.json。"""

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from sources.juejin import fetch as fetch_juejin

DATA_DIR = Path(__file__).resolve().parent.parent / "source" / "data"
OUTPUT = DATA_DIR / "trending.json"
MAX_ARTICLES = 30


def main():
    session = requests.Session()
    if platform.system() == "Windows":
        session.verify = False  # Windows SSL 证书兼容

    articles = []
    try:
        articles.extend(fetch_juejin(session))
        print(f"掘金: {len(articles)} 篇")
    except Exception as e:
        print(f"掘金 抓取失败: {e}", file=sys.stderr)

    # 按 score 降序排列，取前 N 篇
    articles.sort(key=lambda a: a["score"], reverse=True)
    articles = articles[:MAX_ARTICLES]

    now = datetime.now(timezone.utc)
    result = {
        "updated_at": now.isoformat(),
        "articles": articles,
    }

    # 写入当前热文
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写入 {OUTPUT}，共 {len(articles)} 篇文章")


if __name__ == "__main__":
    main()
