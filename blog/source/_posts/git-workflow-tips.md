---
title: Git 工作流最佳实践
date: 2026-06-06 09:00:00
tags:
  - Git
  - 版本控制
  - 工程化
categories:
  - 开发工具
---

## 为什么要规范 Git 工作流？

规范的 Git 工作流能让团队协作更顺畅，代码历史更清晰，问题追溯更容易。

<!-- more -->

## Commit 规范

使用 Conventional Commits 格式：

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

常用 type：
- `feat` - 新功能
- `fix` - 修复 bug
- `docs` - 文档更新
- `style` - 代码格式（不影响功能）
- `refactor` - 重构
- `test` - 测试相关
- `chore` - 构建/工具链

示例：
```bash
git commit -m "feat(auth): add JWT token refresh mechanism"
git commit -m "fix(api): handle null response in user endpoint"
git commit -m "docs: update README with setup instructions"
```

## 分支策略

```
main (production)
  │
  ├── develop (开发主线)
  │     │
  │     ├── feature/user-auth
  │     ├── feature/search
  │     └── feature/trending
  │
  └── hotfix/critical-bug
```

- `main` - 生产环境，始终可部署
- `develop` - 开发主线，功能合并到这里
- `feature/*` - 功能分支，从 develop 分出
- `hotfix/*` - 紧急修复，从 main 分出

## PR 最佳实践

1. **小而专注** - 一个 PR 只做一件事
2. **清晰描述** - 说明做了什么、为什么做
3. **关联 Issue** - 使用 `Closes #123` 自动关闭
4. **自审代码** - 提交前自己先 review 一遍
5. **保持绿色** - CI 通过后再请求 review
