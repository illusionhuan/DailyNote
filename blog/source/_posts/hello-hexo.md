---
title: 使用 Hexo + Butterfly 搭建个人博客
date: 2026-06-08 10:00:00
tags:
  - Hexo
  - 博客搭建
categories:
  - 技术教程
---

## 为什么选择 Hexo？

Hexo 是一个基于 Node.js 的静态站点生成器，特别适合搭建个人博客：

- **速度快** - 几百篇文章也能在几秒内完成构建
- **Markdown 驱动** - 用 Markdown 写作，专注内容
- **丰富的主题和插件** - 中文社区尤其活跃
- **易于部署** - 配合 GitHub Pages 实现免费托管

<!-- more -->

## 为什么选择 Butterfly 主题？

Butterfly 是 Hexo 生态中功能最全面的主题之一：

1. **内置搜索** - 配合 hexo-generator-searchdb，无需第三方服务
2. **暗色模式** - 一键切换，支持跟随系统
3. **卡片布局** - 首页文章展示美观
4. **侧边栏** - 最新文章、分类、标签云、归档一应俱全
5. **代码高亮** - 多种主题可选，支持复制按钮
6. **响应式** - 移动端体验良好

## 快速开始

```bash
# 安装 Hexo
npm install -g hexo-cli

# 创建站点
hexo init my-blog
cd my-blog

# 安装 Butterfly 主题
npm install hexo-theme-butterfly --save

# 启动本地预览
hexo server
```

## 配置要点

Butterfly 使用覆盖式配置，创建 `_config.butterfly.yml` 即可自定义，不影响主题升级：

```yaml
# _config.butterfly.yml
menu:
  首页: / || fas fa-home
  归档: /archives/ || fas fa-archive
  标签: /tags/ || fas fa-tags

darkmode:
  enable: true
  button: true
```

更多配置请参考 [Butterfly 官方文档](https://butterfly.js.org/)。
