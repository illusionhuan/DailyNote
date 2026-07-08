# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指引。

## 项目概述

中文个人技术博客，基于 Hexo 8 + Butterfly 主题构建，部署到 GitHub Pages。已集成全网技术热文聚合功能（掘金数据源，GitHub Actions 每天自动抓取）和每日测试功能（错题本 + localStorage 持久化）。

## 常用命令

所有命令在 `blog/` 目录下执行：

```bash
hexo server                    # 本地预览，http://localhost:4000（支持热更新）
hexo new "文章标题"             # 新建文章，生成在 source/_posts/
hexo clean && hexo generate    # 清理并构建静态文件到 public/
hexo deploy                    # 部署到 GitHub Pages
```

端口 4000 可能被占用——先用 `netstat -ano | grep 4000` 查找进程并 kill，再重启。

## 技术栈

| 层面 | 技术 | 作用 |
|------|------|------|
| 静态站点生成器 | Hexo 8.1.2 | 将 Markdown 文章编译为静态 HTML/CSS/JS |
| 主题 | Butterfly 5.5.4 | 提供 UI 框架：卡片布局、暗色模式、搜索、侧边栏、TOC、代码高亮 |
| 搜索插件 | hexo-generator-searchdb | 生成本地搜索索引 JSON，供 Butterfly 内置搜索 UI 消费 |
| RSS 插件 | hexo-generator-feed | 生成 atom.xml 订阅源 |
| SEO 插件 | hexo-generator-sitemap | 生成 sitemap.xml 供搜索引擎收录 |
| 部署 | GitHub Actions + GitHub Pages | push 到 main 分支时自动构建并部署 |
| 热文抓取 | Python 3 | 调用掘金 API 抓取中文技术热文，输出到 source/data/trending.json |

## 架构说明

```
DailyNote/                       # Git 仓库根目录
├── CLAUDE.md                    # 本文件
├── 博客网站需求文档.md            # 需求文档，含功能清单和进度标记
├── .github/
│   ├── dependabot.yml           # npm 依赖自动更新
│   └── workflows/
│       ├── hexo-deploy.yml      # GitHub Pages 自动部署（必须在仓库根目录）
│       └── fetch_trending.yml   # 热文抓取定时任务（每天 UTC 0:00/12:00）
└── blog/                        # Hexo 项目根目录（所有开发在此进行）
    ├── _config.yml              # Hexo 站点级配置
    ├── _config.butterfly.yml    # Butterfly 主题配置（覆盖式）
    ├── package.json             # Node.js 依赖声明
    ├── package-lock.json        # npm 锁定文件
    ├── fetch_scripts/           # 热文抓取脚本（掘金，不在 scripts/ 避免 Hexo 加载）
    └── source/                  # 源文件目录（构建时复制到 public/）
        ├── _posts/              # 博客文章（Markdown）
        ├── data/
        │   ├── trending.json    # 当前热文数据（掘金中文技术文章）
        │   └── quiz.json        # 每日测试题库（题目、选项、答案、解析）
        ├── css/
        │   ├── carousel.css     # 全站轮播样式（首页 + 所有页面）
        │   ├── gradient.css     # 全局渐变色主题覆盖（#7CABBA 色系）
        │   └── custom-pages.css # 归档时间线美化 + 分类卡片样式
        ├── js/carousel.js       # 全站轮播逻辑（class 检测，覆盖所有页面）
        ├── images/              # 7 张风景图（轮播 + 页面背景）
        ├── pluginsSrc/          # 第三方库本地副本（CDN 策略为 local）
        ├── trending/            # 热文榜页面（轮播背景 + 暗色模式）
        ├── quiz/                # 每日测试页面（答题 + 错题本，localStorage 持久化）
        ├── classify/            # 分类页面（分类卡片 + 标签云 tab 切换）
        ├── categories/          # 分类数据页（供 classify 页面 JS 抓取）
        ├── tags/                # 标签数据页（供 classify 页面 JS 抓取）
        └── about/               # 关于页面（轮播背景）
```

## 配置文件详解

### `_config.yml`（Hexo 站点配置）

控制站点级别的行为，主要配置项：

- **站点信息**（title/subtitle/description/author/language）：影响页面标题、SEO meta 标签
- **URL**（url/root/permalink）：`root: /DailyNote/` 部署在 GitHub Pages 项目子目录，所有内部链接以 `/DailyNote/` 开头
- **主题**（theme: butterfly）：指定使用 Butterfly 主题
- **搜索**（search）：配合 hexo-generator-searchdb 生成搜索索引
- **RSS**（feed）：生成 atom.xml 订阅源
- **Sitemap**（sitemap）：生成 sitemap.xml 供搜索引擎爬取
- **代码高亮**（highlight/prismjs）：使用 highlight.js 渲染代码块
- **分页**（per_page）：每页显示 10 篇文章

### `_config.butterfly.yml`（Butterfly 主题配置）

控制主题的视觉和交互，通过覆盖式配置避免修改 node_modules 中的源文件。主要配置段：

- **nav / menu**：导航栏 logo、固定状态、菜单项（首页/归档/分类/热文榜/每日测试/关于）
- **code_blocks**：代码块样式（darker 主题、mac 风格、复制按钮）
- **subtitle**：首页副标题打字机效果
- **index_layout / index_post_content**：首页文章卡片布局方式和摘要长度
- **toc**：文章目录导航（启用、编号、滚动百分比）
- **post_copyright**：文章底部版权声明（CC BY-NC-SA 4.0）
- **aside**：侧边栏配置（作者卡片、公告、最新文章、分类、标签云、归档、站点信息）
- **darkmode**：暗色模式开关和切换按钮
- **theme_color**：主题色配置（主色 #7CABBA，深色 #5A8C9C，浅色 #9CC5D0，由 gradient.css 全局覆盖）
- **search**：本地搜索配置（Butterfly 内置 UI）
- **inject**：向页面 head/bottom 注入自定义 CSS/JS（轮播、渐变主题、归档/分类美化）
- **lazyload**：图片懒加载（全站生效，带模糊占位）
- **busuanzi**：不蒜子阅读统计（站点 UV/PV、页面 PV）
- **CDN**：资源加载策略（内部和第三方均为 local，第三方库存放在 source/pluginsSrc/）

## 关键模式

- 文章使用 YAML frontmatter 声明 `title`、`date`、`tags`、`categories`、`description`、`cover`
- Butterfly 配置写在 `_config.butterfly.yml`（覆盖文件），不要改 node_modules 内的主题配置
- 主题色通过 `gradient.css` 全局覆盖（基础色 #7CABBA，深色 #5A8C9C，浅色 #9CC5D0），包含亮色和暗色模式适配
- 轮播 JS 通过 header 的 class 检测页面类型：`full_page`（首页）、`not-home-page`（归档/分类/标签等）、`post-bg`（文章页），覆盖全站所有页面
- 根路径为 `/DailyNote/`（GitHub Pages 项目站点 URL），所有内部资源路径以 `/DailyNote/` 开头（如 `/DailyNote/images/landscape1.jpg`）
- 自定义 inject 中的 CSS/JS 路径也必须使用 `/DailyNote/` 前缀
- hexo-generator-searchdb 生成搜索索引，Butterfly 内置搜索 UI 直接消费
- 静态资源（图片/CSS/JS）放在 `source/` 下，构建时自动复制到 `public/`
- 第三方库（fancybox、fontawesome、typed.js 等）通过 npm 安装后复制到 `source/pluginsSrc/`，CDN 策略设为 `local`

## 开发状态

Phase 1-3 均已完成。Phase 4（打磨运维）部分完成。详见 `博客网站需求文档.md`。

### 已完成优化（2026-07-09）

1. **图片优化**：51MB → 3.3MB（压缩率 93.5%）
2. **配置路径统一**：解决双重路径 bug，统一路径格式
3. **删除热文历史归档**：简化 fetch_trending.py（62 行 → 46 行）
4. **性能优化**：CSS/JS 压缩 34%，构建产物 61MB → 14MB

### 当前待做

1. 自定义域名绑定（可选）

### 已知配置

- Python 抓取脚本在 `blog/fetch_scripts/`（不在 `scripts/`，Hexo 会尝试加载为 JS）
- 头像路径：`/images/9-tuya.jpg`
- 热文数据源：仅掘金（中文技术文章）
- 轮播图片：`images/landscape1-7.jpg`（7 张，全站共用）

## GitHub Pages 部署

### 部署流程

1. GitHub Actions workflow 位于 `.github/workflows/hexo-deploy.yml`（必须在仓库根目录）
2. push 到 `main` 分支自动触发构建和部署
3. 构建过程：在 `blog/` 子目录执行 `npm ci` → `npx hexo generate`
4. 部署产物：`blog/public/` 目录上传到 GitHub Pages

### 关键配置

- **Node.js 版本**：24（GitHub Actions 已弃用 Node.js 20）
- **环境变量**：`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"` 消除弃用警告
- **工作目录**：workflow 中使用 `working-directory: blog` 指定 Hexo 项目目录
- **站点 URL**：`https://illusionhuan.github.io/DailyNote/`

### 注意事项

- `.github/workflows/` 必须在仓库根目录，GitHub 不会识别子目录中的 workflow
- `package-lock.json` 必须提交到仓库（`npm ci` 需要）
- `node_modules/` 和 `public/` 在 `.gitignore` 中已忽略

### 踩坑记录：root 路径与 GitHub Pages 部署

GitHub Pages 项目站点（非 `<user>.github.io` 仓库）的 URL 格式为 `https://<user>.github.io/<仓库名>/`。本仓库名为 `DailyNote`，因此站点 URL 为 `https://illusionhuan.github.io/DailyNote/`。

**曾犯的错误：** 先设为 `root: /blog/`（部署到 /blog/ 子目录），后改为 `root: /`（部署到根目录），两次都导致线上 CSS/JS 404。原因：
1. `root` 决定 HTML 中所有资源引用的路径前缀
2. GitHub Pages 上传 `blog/public/` 作为部署产物，CSS 文件在产物根目录的 `css/` 下
3. 站点实际在 `/DailyNote/`，所以 `root` 必须是 `/DailyNote/`

**涉及的配置点（修改 root 时必须同步更新）：**
- `_config.yml` 中的 `url` 和 `root`
- `_config.butterfly.yml` 中 `inject` 部分的自定义 CSS/JS 路径
- `source/js/carousel.js` 中的图片路径和 URL 检测正则
