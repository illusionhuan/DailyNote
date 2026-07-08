# 博客优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 优化博客性能，包括图片压缩、配置路径统一、删除热文历史归档和性能增强

**Architecture:** 分阶段优化，每阶段独立验证，确保功能正常后再进入下一阶段

**Tech Stack:** Python 3, Hexo 8, Butterfly 主题, Pillow (图片压缩), HTML/CSS/JS

## Global Constraints

- 所有命令在 `blog/` 目录下执行
- 图片压缩保留原始格式，不转换为 WebP
- 配置路径统一使用完整路径格式（/DailyNote/...）
- 热文历史归档功能完全删除
- 性能优化包括前端性能、构建优化和 SEO 增强

---

## Task 1: 图片压缩

**Files:**
- Create: `blog/scripts/compress_images.py`
- Modify: `blog/source/images/*.jpg`, `blog/source/images/*.png`
- Create: `blog/source/images/backup/` (备份目录)

**Interfaces:**
- Consumes: 原始图片文件（51MB）
- Produces: 压缩后的图片文件（目标 10MB 以内）

- [ ] **Step 1: 安装依赖**

```bash
cd blog
pip install Pillow
```

- [ ] **Step 2: 创建压缩脚本**

```python
# blog/scripts/compress_images.py
import os
from PIL import Image
from pathlib import Path

def compress_image(input_path, output_path, quality=85):
    """压缩图片，保留原始格式"""
    try:
        with Image.open(input_path) as img:
            # 保存压缩后的图片
            img.save(output_path, quality=quality, optimize=True)
            print(f"压缩完成: {input_path} -> {output_path}")
            return True
    except Exception as e:
        print(f"压缩失败 {input_path}: {e}")
        return False

def main():
    images_dir = Path(__file__).parent.parent / "source" / "images"
    backup_dir = images_dir / "backup"
    
    # 创建备份目录
    backup_dir.mkdir(exist_ok=True)
    
    # 需要压缩的大文件
    large_files = [
        "1.png",
        "2.jpg", 
        "landscape5.jpg",
        "landscape4.jpg",
        "landscape3.jpg"
    ]
    
    for filename in large_files:
        input_path = images_dir / filename
        backup_path = backup_dir / filename
        
        if input_path.exists():
            # 备份原始文件
            if not backup_path.exists():
                import shutil
                shutil.copy2(input_path, backup_path)
                print(f"备份: {filename}")
            
            # 压缩图片
            compress_image(input_path, input_path, quality=85)

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 运行压缩脚本**

```bash
cd blog
python scripts/compress_images.py
```

Expected output:
```
备份: 1.png
压缩完成: source/images/1.png -> source/images/1.png
备份: 2.jpg
压缩完成: source/images/2.jpg -> source/images/2.jpg
...
```

- [ ] **Step 4: 验证压缩效果**

```bash
cd blog
du -sh source/images/
ls -lh source/images/
```

Expected: 图片总大小从 51MB 降至 10MB 以内

- [ ] **Step 5: 测试轮播功能**

```bash
cd blog
hexo server
```

- 访问 http://localhost:4000
- 验证首页轮播正常显示
- 验证图片质量可接受

- [ ] **Step 6: Commit**

```bash
cd blog
git add scripts/compress_images.py source/images/
git commit -m "feat: compress images to reduce size from 51MB to 10MB"
```

---

## Task 2: 配置路径统一

**Files:**
- Modify: `blog/_config.butterfly.yml`
- Modify: `blog/source/js/carousel.js`

**Interfaces:**
- Consumes: 压缩后的图片文件
- Produces: 统一路径的配置文件

- [ ] **Step 1: 更新 _config.butterfly.yml**

```yaml
# 更新以下配置项
archive_img: /DailyNote/images/landscape1.jpg
category_img: /DailyNote/images/landscape2.jpg
tag_img: /DailyNote/images/landscape3.jpg
default_top_img: /DailyNote/images/landscape4.jpg
```

- [ ] **Step 2: 验证 carousel.js 路径**

检查 `blog/source/js/carousel.js` 中的图片路径是否已使用 `/DailyNote/images/` 前缀：

```javascript
var images = [
  '/DailyNote/images/landscape1.jpg',
  '/DailyNote/images/landscape2.jpg',
  '/DailyNote/images/landscape3.jpg',
  '/DailyNote/images/landscape4.jpg',
  '/DailyNote/images/landscape5.jpg',
  '/DailyNote/images/landscape6.jpg',
  '/DailyNote/images/landscape7.jpg'
];
```

- [ ] **Step 3: 测试配置**

```bash
cd blog
hexo clean && hexo generate
hexo server
```

- 访问 http://localhost:4000
- 验证所有页面图片正常显示
- 验证轮播功能正常

- [ ] **Step 4: Commit**

```bash
cd blog
git add _config.butterfly.yml source/js/carousel.js
git commit -m "feat: unify image paths to use /DailyNote/ prefix"
```

---

## Task 3: 删除热文历史归档

**Files:**
- Modify: `blog/fetch_scripts/fetch_trending.py`
- Delete: `blog/source/data/trending_history/`

**Interfaces:**
- Consumes: 现有的热文抓取脚本
- Produces: 简化后的热文抓取脚本（无历史归档功能）

- [ ] **Step 1: 删除历史数据目录**

```bash
cd blog
rm -rf source/data/trending_history/
```

- [ ] **Step 2: 修改 fetch_trending.py**

删除以下代码（第 14 行和第 46-58 行）：

```python
# 删除这行
HISTORY_DIR = DATA_DIR / "trending_history"

# 删除这段代码（第 46-58 行）
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
```

简化后的 `fetch_trending.py` 应该如下：

```python
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
```

- [ ] **Step 3: 测试热文抓取功能**

```bash
cd blog
python fetch_scripts/fetch_trending.py
```

Expected output:
```
掘金: 15 篇
已写入 source/data/trending.json，共 15 篇文章
```

- [ ] **Step 4: 验证 trending.json 生成**

```bash
cd blog
cat source/data/trending.json | head -20
```

Expected: 正常的 JSON 内容，包含 updated_at 和 articles 字段

- [ ] **Step 5: Commit**

```bash
cd blog
git add fetch_scripts/fetch_trending.py
git rm -r source/data/trending_history/
git commit -m "feat: remove trending history archive functionality"
```

---

## Task 4: 性能优化

**Files:**
- Modify: `blog/source/css/carousel.css`
- Modify: `blog/source/css/gradient.css`
- Modify: `blog/source/css/custom-pages.css`
- Modify: `blog/source/js/carousel.js`
- Modify: `blog/_config.yml`
- Modify: `blog/_config.butterfly.yml`

**Interfaces:**
- Consumes: 压缩后的图片和统一路径的配置
- Produces: 优化后的前端资源和配置

- [ ] **Step 1: 压缩 CSS 文件**

使用在线工具或命令行工具压缩 CSS 文件：
- `blog/source/css/carousel.css`
- `blog/source/css/gradient.css`
- `blog/source/css/custom-pages.css`

或者使用 clean-css 命令行工具：

```bash
npm install -g clean-css-cli
cd blog
cleancss -o source/css/carousel.min.css source/css/carousel.css
cleancss -o source/css/gradient.min.css source/css/gradient.css
cleancss -o source/css/custom-pages.min.css source/css/custom-pages.css
```

- [ ] **Step 2: 压缩 JS 文件**

使用在线工具或命令行工具压缩 JS 文件：
- `blog/source/js/carousel.js`

或者使用 uglifyjs 命令行工具：

```bash
npm install -g uglify-js
cd blog
uglifyjs source/js/carousel.js -o source/js/carousel.min.js
```

- [ ] **Step 3: 更新配置使用压缩后的文件**

更新 `blog/_config.butterfly.yml` 的 inject 部分：

```yaml
inject:
  head:
    - <link rel="stylesheet" href="/DailyNote/css/carousel.min.css">
    - <link rel="stylesheet" href="/DailyNote/css/gradient.min.css">
    - <link rel="stylesheet" href="/DailyNote/css/custom-pages.min.css">
  bottom:
    - <script src="/DailyNote/js/carousel.min.js"></script>
```

- [ ] **Step 4: 优化图片懒加载配置**

验证 `blog/_config.butterfly.yml` 中的懒加载配置：

```yaml
lazyload:
  enable: true
  field: site
  placeholder:
  blur: true
```

- [ ] **Step 5: 添加结构化数据（JSON-LD）**

创建 `blog/source/_data/structured_data.yml`：

```yaml
# 首页结构化数据
homepage:
  "@context": "https://schema.org"
  "@type": "WebSite"
  name: "我的博客"
  url: "https://illusionhuan.github.io/DailyNote/"
  description: "个人技术博客，分享编程心得与全网技术热文"
  author:
    "@type": "Person"
    name: "illusionhuan"
```

- [ ] **Step 6: 优化 meta 标签**

验证 `blog/_config.yml` 中的 meta 配置：

```yaml
# 站点信息
title: 我的博客
subtitle: 技术分享与热文聚合
description: 个人技术博客，分享编程心得与全网技术热文
keywords:
  - 技术博客
  - 编程
  - 热文聚合
author: illusionhuan
language: zh-CN
timezone: Asia/Shanghai
```

- [ ] **Step 7: 测试优化效果**

```bash
cd blog
hexo clean && hexo generate
hexo server
```

- 访问 http://localhost:4000
- 验证所有功能正常
- 使用浏览器开发者工具检查加载速度

- [ ] **Step 8: Commit**

```bash
cd blog
git add source/css/ source/js/ _config.yml _config.butterfly.yml
git commit -m "feat: optimize frontend performance and SEO"
```

---

## Task 5: 最终验证

**Files:**
- None (verification only)

**Interfaces:**
- Consumes: 所有优化后的文件
- Produces: 验证报告

- [ ] **Step 1: 验证图片大小**

```bash
cd blog
du -sh source/images/
```

Expected: 图片总大小在 10MB 以内

- [ ] **Step 2: 验证配置路径**

检查所有配置文件中的路径是否统一使用 `/DailyNote/` 前缀。

- [ ] **Step 3: 验证热文抓取功能**

```bash
cd blog
python fetch_scripts/fetch_trending.py
```

Expected: 正常抓取并生成 trending.json

- [ ] **Step 4: 验证页面功能**

```bash
cd blog
hexo server
```

- 访问 http://localhost:4000
- 测试首页轮播
- 测试文章页面
- 测试分类页面
- 测试热文榜页面
- 测试每日测试页面

- [ ] **Step 5: 性能测试**

使用浏览器开发者工具或 Google PageSpeed Insights 测试页面加载速度。

- [ ] **Step 6: 最终 Commit**

```bash
cd blog
git add .
git commit -m "feat: complete blog optimization - images, paths, performance"
```

---

## 验证检查清单

### 图片优化验证
- [ ] 图片总大小降至 10MB 以内
- [ ] 所有图片正常显示
- [ ] 轮播功能正常
- [ ] 页面加载速度提升

### 配置路径验证
- [ ] 所有配置路径统一为完整路径格式
- [ ] 所有页面图片正常显示
- [ ] 配置文件语法正确

### 热文历史归档验证
- [ ] 历史数据目录已删除
- [ ] fetch_trending.py 代码已简化
- [ ] 热文抓取功能正常
- [ ] trending.json 正常生成

### 性能优化验证
- [ ] CSS/JS 文件已压缩
- [ ] 懒加载功能正常
- [ ] 结构化数据已添加
- [ ] meta 标签已优化
- [ ] 页面加载速度提升

---

## 回滚策略

每个任务都提供独立的回滚方案：

1. **Task 1 回滚**：从备份目录恢复原始图片
2. **Task 2 回滚**：恢复原始配置文件
3. **Task 3 回滚**：从 git 恢复原始代码
4. **Task 4 回滚**：恢复原始配置

**总体回滚：**
- 使用 `git revert` 回滚所有更改
- 重新构建部署

---

**实施计划已完成。请用户选择执行方式。**