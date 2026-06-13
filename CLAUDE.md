# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指引。

## 项目概述

中文个人技术博客，基于 Hexo 8 + Butterfly 主题构建，部署到 GitHub Pages。计划集成全网技术热文聚合功能。

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
| 热文抓取（计划中） | Python 3 | 调用各平台 API 抓取热文，输出到 source/_data/trending.json |

## 架构说明

```
DailyNote/
├── CLAUDE.md                    # 本文件
├── 中文博客需求文档.md            # 需求文档，含功能清单和进度标记
└── blog/                        # Hexo 项目根目录（所有开发在此进行）
    ├── _config.yml              # Hexo 站点级配置
    ├── _config.butterfly.yml    # Butterfly 主题配置（覆盖式）
    ├── package.json             # Node.js 依赖声明
    ├── source/                  # 源文件目录（构建时复制到 public/）
    │   ├── _posts/              # 博客文章（Markdown）
    │   ├── _data/trending.json  # 热文数据（Python 脚本生成）
    │   ├── css/carousel.css     # 自定义轮播样式
    │   ├── js/carousel.js       # 自定义轮播逻辑
    │   ├── images/              # 图片资源
    │   ├── trending/            # 热文榜页面
    │   ├── search/              # 搜索页面
    │   └── about/               # 关于页面
    ├── .github/workflows/
    │   └── hexo-deploy.yml      # GitHub Pages 自动部署
    └── themes/                  # 空目录（Butterfly 通过 npm 安装）
```

## 配置文件详解

### `_config.yml`（Hexo 站点配置）

控制站点级别的行为，主要配置项：

- **站点信息**（title/subtitle/description/author/language）：影响页面标题、SEO meta 标签
- **URL**（url/root/permalink）：`root: /blog/` 表示部署在子路径下，所有内部链接需加 `/blog/` 前缀
- **主题**（theme: butterfly）：指定使用 Butterfly 主题
- **搜索**（search）：配合 hexo-generator-searchdb 生成搜索索引
- **RSS**（feed）：生成 atom.xml 订阅源
- **Sitemap**（sitemap）：生成 sitemap.xml 供搜索引擎爬取
- **代码高亮**（highlight/prismjs）：使用 highlight.js 渲染代码块
- **分页**（per_page）：每页显示 10 篇文章

### `_config.butterfly.yml`（Butterfly 主题配置）

控制主题的视觉和交互，通过覆盖式配置避免修改 node_modules 中的源文件。主要配置段：

- **nav / menu**：导航栏 logo、固定状态、菜单项（首页/归档/标签/分类/热文榜/搜索/关于）
- **code_blocks**：代码块样式（darker 主题、mac 风格、复制按钮）
- **subtitle**：首页副标题打字机效果
- **index_layout / index_post_content**：首页文章卡片布局方式和摘要长度
- **toc**：文章目录导航（启用、编号、滚动百分比）
- **post_copyright**：文章底部版权声明（CC BY-NC-SA 4.0）
- **aside**：侧边栏配置（作者卡片、公告、最新文章、分类、标签云、归档、站点信息）
- **darkmode**：暗色模式开关和切换按钮
- **theme_color**：主题色配置（主色 #22A2C3 及其深浅变体）
- **search**：本地搜索配置（Butterfly 内置 UI）
- **inject**：向页面 head/bottom 注入自定义 CSS/JS（当前注入轮播样式和脚本）
- **lazyload**：图片懒加载（全站生效，带模糊占位）
- **busuanzi**：不蒜子阅读统计（站点 UV/PV、页面 PV）
- **CDN**：资源加载策略（内部 local，第三方 jsdelivr）

## 关键模式

- 文章使用 YAML frontmatter 声明 `title`、`date`、`tags`、`categories`、`description`、`cover`
- Butterfly 配置写在 `_config.butterfly.yml`（覆盖文件），不要改 node_modules 内的主题配置
- 自定义 JS 通过 `header.classList.contains('full_page')` 判断是否为首页（body 标签没有 home class）
- 根路径为 `/blog/`，所有内部资源路径必须带此前缀（如 `/blog/images/landscape1.jpg`）
- hexo-generator-searchdb 生成搜索索引，Butterfly 内置搜索 UI 直接消费
- 静态资源（图片/CSS/JS）放在 `source/` 下，构建时自动复制到 `public/`

## 开发状态

Phase 1（基础博客）已完成。详见 `中文博客需求文档.md` 中的功能清单和进度标记。下一步是 Phase 2：Python 热文抓取脚本。
