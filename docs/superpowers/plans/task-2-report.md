# Task 2: 配置路径统一 - 执行报告

## 状态: DONE

## 执行的步骤

### 1. 初始分析

读取 `_config.butterfly.yml` 和 `carousel.js`，发现：
- `carousel.js` 已使用 `/DailyNote/images/` 前缀（正确，直接由浏览器请求）
- `_config.butterfly.yml` 中 `archive_img`/`category_img`/`tag_img`/`default_top_img` 已使用 `/DailyNote/images/` 前缀
- `avatar.img` 使用 `/images/9-tuya.jpg`（无 `/DailyNote/` 前缀）

### 2. 发现关键问题

构建后检查生成的 HTML，发现**双重路径问题**：
- `background-image: url(/DailyNote/DailyNote/images/landscape1.jpg)`
- `data-lazy-src="/DailyNote/DailyNote/images/9-tuya.jpg"`
- `og:image content="https://illusionhuan.github.io/DailyNote/DailyNote/images/9-tuya.jpg"`

**根因分析：** Butterfly 主题的 `getBgPath` helper 使用 Hexo 的 `url_for()` 函数，该函数会自动将 `_config.yml` 中的 `root: /DailyNote/` 拼接到路径前面。因此配置中写 `/DailyNote/images/...` 会导致输出 `/DailyNote/DailyNote/images/...`。

### 3. 修复所有路径

**`_config.butterfly.yml`：**
```yaml
# 修改前（双重路径）
archive_img: /DailyNote/images/landscape1.jpg
category_img: /DailyNote/images/landscape2.jpg
tag_img: /DailyNote/images/landscape3.jpg
default_top_img: /DailyNote/images/landscape4.jpg

# 修改后（url_for 自动添加 /DailyNote/ 前缀）
archive_img: /images/landscape1.jpg
category_img: /images/landscape2.jpg
tag_img: /images/landscape3.jpg
default_top_img: /images/landscape4.jpg
```

**页面 frontmatter `top_img`：**
- `about/index.md`: `/DailyNote/images/landscape6.jpg` -> `/images/landscape6.jpg`
- `classify/index.md`: `/DailyNote/images/landscape2.jpg` -> `/images/landscape2.jpg`
- `quiz/index.md`: `/DailyNote/images/landscape3.jpg` -> `/images/landscape3.jpg`
- `trending/index.md`: `/DailyNote/images/landscape7.jpg` -> `/images/landscape7.jpg`

### 4. 路径策略确认

| 场景 | 路径格式 | 原因 |
|------|----------|------|
| `_config.butterfly.yml` 图片配置 | `/images/...` | url_for 自动添加 root 前缀 |
| 页面 frontmatter `top_img` | `/images/...` | url_for 自动添加 root 前缀 |
| `_config.butterfly.yml` inject CSS/JS | `/DailyNote/...` | 原始 HTML，不经过 url_for |
| `carousel.js` 图片路径 | `/DailyNote/images/...` | 直接由浏览器请求，不经过 url_for |

### 5. 验证

- `hexo clean && hexo generate` 构建成功（249 文件）
- 无 `/DailyNote/DailyNote/` 双重路径
- 归档页 header: `background-image: url(/DailyNote/images/landscape1.jpg)` 正确
- 关于页 header: `background-image: url(/DailyNote/images/landscape6.jpg)` 正确
- 头像: `data-lazy-src="/DailyNote/images/9-tuya.jpg"` 正确
- og:image: `https://illusionhuan.github.io/DailyNote/images/9-tuya.jpg` 正确
- inject CSS/JS 路径正确

## 遇到的问题及解决方案

**问题：** 原始配置中 `archive_img` 等已使用 `/DailyNote/images/` 前缀，导致 Butterfly 主题通过 `url_for()` 处理后产生双重路径 `/DailyNote/DailyNote/images/`。

**解决方案：** 将所有经过 `url_for()` 处理的路径改为不带 `/DailyNote/` 前缀的格式（`/images/...`），让 `url_for()` 自动添加正确的 root 前缀。

## 提交的 commit hash

`fb4f60c` - fix: remove double /DailyNote/ prefix from image paths

## 测试结果摘要

- 构建成功：249 文件生成
- 无双重路径问题
- 所有页面图片路径正确
- carousel.js 轮播路径正确（7 张图片）
- inject CSS/JS 路径正确
- 头像和 og:image 路径正确
