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
HISTORY_DIR = DATA_DIR / "trending_history"
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

    # 保存历史快照
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    date_str = now.strftime("%Y-%m-%d")
    snapshot = HISTORY_DIR / f"{date_str}.json"
    snapshot.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"历史快照: {snapshot}")

    # 更新 manifest（可用日期列表）
    manifest_path = HISTORY_DIR / "manifest.json"
    dates = sorted(set(
        p.stem for p in HISTORY_DIR.glob("*.json") if p.name != "manifest.json"
    ), reverse=True)
    manifest_path.write_text(json.dumps({"dates": dates}, ensure_ascii=False), encoding="utf-8")
    print(f"manifest 已更新，共 {len(dates)} 个日期")


if __name__ == "__main__":
    main()
