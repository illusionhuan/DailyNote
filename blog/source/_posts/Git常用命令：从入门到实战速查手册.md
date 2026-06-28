---
title: "Git常用命令：从入门到实战速查手册"
date: 2026-06-28 18:00:00
tags:
  - Git
  - 版本控制
  - 命令行
categories:
  - 开发工具
---

## 前言

Git 是每个开发者的必备工具，但日常真正用到的命令远比想象中集中。本文按使用场景分类，系统梳理从初始化仓库到高级操作的常用 Git 命令，每个命令附带实际用法和关键参数，适合作为速查手册随时翻阅。

<!-- more -->

## 一、仓库初始化与配置

### 1.1 创建仓库

```bash
git init                           # 在当前目录初始化空仓库
git init my-project                # 创建并初始化指定目录
git clone https://github.com/user/repo.git   # 克隆远程仓库
git clone https://github.com/user/repo.git my-dir  # 克隆到指定目录
git clone --depth 1 URL            # 浅克隆（只拉最新一次提交，节省时间）
```

### 1.2 全局配置

```bash
git config --global user.name "Your Name"       # 设置用户名
git config --global user.email "you@example.com" # 设置邮箱
git config --global core.editor vim              # 设置默认编辑器
git config --global init.defaultBranch main      # 设置默认分支名
git config --list                                # 查看所有配置
git config --global --unset user.name            # 删除某项配置
```

配置文件位置：
- `--global`：`~/.gitconfig`（用户级）
- `--local`：`.git/config`（仓库级，优先级最高）
- `--system`：`/etc/gitconfig`（系统级）

## 二、日常操作

### 2.1 查看状态

```bash
git status                     # 查看工作区状态
git status -s                  # 简洁模式（M=修改, A=新增, D=删除, ??=未跟踪）
git diff                       # 查看未暂存的修改
git diff --staged              # 查看已暂存但未提交的修改
git diff HEAD                  # 查看所有未提交的修改（含已暂存）
git diff branch1..branch2      # 比较两个分支的差异
git diff --name-only branch1..branch2  # 只显示文件名
git log                        # 查看提交历史
git log --oneline              # 单行简洁模式
git log --oneline -10          # 最近 10 条
git log --graph --oneline      # 图形化显示分支合并历史
git log --author="name"        # 按作者过滤
git log --since="2026-01-01"   # 按日期过滤
git log -p file.txt            # 查看某个文件的修改历史
git blame file.txt             # 逐行查看最后修改人和时间
```

### 2.2 添加与提交

```bash
git add file.txt               # 暂存指定文件
git add .                      # 暂存当前目录所有修改
git add -p                     # 交互式暂存（逐块选择是否暂存）
git commit -m "message"        # 提交并写说明
git commit -am "message"       # 跳过 add，直接提交已跟踪文件的修改
git commit --amend             # 修改最近一次提交（message 或内容）
git commit --amend --no-edit   # 追加修改到最近一次提交（不改 message）
```

### 2.3 撤销操作

```bash
# 撤销工作区的修改（未 add）
git checkout -- file.txt       # 恢复文件到上次提交的状态
git restore file.txt           # 同上（Git 2.23+ 推荐写法）

# 撤销暂存（已 add，未 commit）
git reset HEAD file.txt        # 取消暂存
git restore --staged file.txt  # 同上（Git 2.23+ 推荐写法）

# 撤销提交（已 commit）
git reset --soft HEAD~1        # 撤销提交，保留修改在暂存区
git reset --mixed HEAD~1       # 撤销提交，保留修改在工作区（默认模式）
git reset --hard HEAD~1        # 撤销提交，丢弃所有修改（慎用！）

# 回退到指定提交
git reset --hard abc123        # 回退到指定 commit hash
git revert abc123              # 创建一个新提交来撤销指定提交（安全）
```

`reset` vs `revert`：

| 操作 | 是否改写历史 | 适用场景 |
|------|-------------|---------|
| `reset` | 是 | 本地还没推送的提交 |
| `revert` | 否 | 已经推送到远程的提交 |

### 2.4 暂存工作区

```bash
git stash                      # 暂存当前修改
git stash push -m "描述"        # 暂存并加说明
git stash list                 # 查看所有暂存记录
git stash pop                  # 恢复最近一次暂存并删除记录
git stash apply                # 恢复最近一次暂存（保留记录）
git stash apply stash@{2}      # 恢复指定暂存
git stash drop stash@{0}       # 删除指定暂存
git stash clear                # 清空所有暂存
```

## 三、分支管理

### 3.1 分支基本操作

```bash
git branch                     # 查看本地分支
git branch -a                  # 查看所有分支（含远程）
git branch feature/login       # 创建分支
git checkout feature/login     # 切换分支
git checkout -b feature/login  # 创建并切换（常用）
git switch feature/login       # 切换分支（Git 2.23+ 推荐）
git switch -c feature/login    # 创建并切换（Git 2.23+ 推荐）
git branch -d feature/login    # 删除分支（已合并才能删）
git branch -D feature/login    # 强制删除分支
git branch -m old-name new-name  # 重命名分支
```

### 3.2 合并与变基

```bash
# merge：合并分支（保留分支历史）
git merge feature/login        # 将 feature/login 合并到当前分支
git merge --no-ff feature/login  # 禁止快进合并（保留分支记录）
git merge --squash feature/login  # 压缩合并（所有改动合为一个提交）

# rebase：变基（线性历史）
git rebase main                # 将当前分支的提交移到 main 之上
git rebase -i HEAD~3           # 交互式变基（修改最近 3 次提交）
git rebase --abort             # 中止变基，回到变基前的状态
git rebase --continue          # 解决冲突后继续变基
```

`merge` vs `rebase`：

| 操作 | 历史记录 | 适用场景 |
|------|---------|---------|
| `merge` | 非线性，保留分支结构 | 团队协作，公共分支 |
| `rebase` | 线性，更干净 | 个人分支，整理提交历史 |

### 3.3 解决冲突

合并或变基产生冲突时，冲突文件中会出现标记：

```
<<<<<<< HEAD
当前分支的内容
=======
要合并进来的分支的内容
>>>>>>> feature/login
```

解决步骤：
1. 编辑冲突文件，删除冲突标记，保留正确内容
2. `git add <冲突文件>` 标记为已解决
3. `git commit`（merge 时）或 `git rebase --continue`（rebase 时）

```bash
git merge --abort               # 放弃合并，回到合并前
git rerere                      # 自动记录冲突解决方案（开启后下次同样冲突自动解决）
```

## 四、远程操作

### 4.1 远程仓库管理

```bash
git remote                     # 查看远程仓库名
git remote -v                  # 查看远程仓库 URL
git remote add origin URL      # 添加远程仓库
git remote set-url origin URL  # 修改远程仓库 URL
git remote remove origin       # 移除远程仓库
```

### 4.2 推送与拉取

```bash
git push origin main           # 推送到远程 main 分支
git push -u origin main        # 推送并设置上游分支（首次推送）
git push                       # 推送到已设置的上游分支
git push --force               # 强制推送（覆盖远程历史，慎用！）
git push --force-with-lease    # 安全的强制推送（远程无新提交才允许）

git pull                       # 拉取并合并（= fetch + merge）
git pull --rebase              # 拉取并变基（= fetch + rebase，推荐）
git fetch                      # 只拉取远程更新，不合并
git fetch --prune              # 拉取并清理已删除的远程分支引用
```

### 4.3 跟踪远程分支

```bash
git branch -u origin/feature   # 当前分支跟踪远程分支
git branch --set-upstream-to=origin/feature local-branch  # 指定本地分支跟踪
git branch -vv                 # 查看分支的跟踪关系
```

## 五、标签管理

```bash
git tag                        # 查看所有标签
git tag v1.0.0                 # 创建轻量标签
git tag -a v1.0.0 -m "release" # 创建附注标签（含说明）
git tag -a v1.0.0 abc123       # 给指定提交打标签
git push origin v1.0.0         # 推送指定标签
git push origin --tags         # 推送所有标签
git tag -d v1.0.0              # 删除本地标签
git push origin --delete v1.0.0  # 删除远程标签
```

## 六、高级操作

### 6.1 Cherry-pick

```bash
git cherry-pick abc123         # 将指定提交应用到当前分支
git cherry-pick abc123 def456  # 挑选多个提交
git cherry-pick abc123..def456 # 挑选一个范围的提交
git cherry-pick --no-commit abc123  # 只应用修改，不自动提交
```

### 6.2 查看引用日志

```bash
git reflog                     # 查看 HEAD 的移动记录（找回丢失的提交）
git reflog show branch-name    # 查看指定分支的移动记录
git reset --hard HEAD@{2}      # 根据 reflog 恢复到之前的状态
```

reflog 是找回误操作的最后防线——即使 `reset --hard` 丢了提交，reflog 里还有记录。

### 6.3 二分查找

```bash
git bisect start               # 开始二分查找
git bisect bad                 # 标记当前版本有 bug
git bisect good v1.0.0         # 标记指定版本正常
# Git 自动切换到中间版本，你测试后继续标记 good/bad
git bisect reset               # 结束二分查找，回到原始状态
```

### 6.4 子模块

```bash
git submodule add URL path     # 添加子模块
git submodule init             # 初始化子模块
git submodule update           # 更新子模块
git clone --recursive URL      # 克隆时自动拉取子模块
git submodule update --remote  # 拉取子模块最新代码
```

### 6.5 清理

```bash
git clean -n                   # 预览将被删除的未跟踪文件
git clean -f                   # 删除未跟踪的文件
git clean -fd                  # 删除未跟踪的文件和目录
git clean -fdx                 # 删除未跟踪的文件、目录和 .gitignore 忽略的文件
```

## 七、实用技巧

### 7.1 别名设置

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --all"
git config --global alias.last "log -1 HEAD"
git config --global alias.unstage "reset HEAD --"
```

### 7.2 .gitignore

```bash
# 忽略所有 .log 文件
*.log

# 忽略 node_modules 目录
node_modules/

# 忽略根目录下的 build 目录
/build/

# 不忽略某个文件
!important.log

# 忽略所有 .pyc 文件
*.pyc
```

已经在跟踪的文件不会被 `.gitignore` 忽略，需要先取消跟踪：

```bash
git rm --cached file.txt       # 取消跟踪但保留本地文件
git rm -r --cached node_modules/
```

### 7.3 常用场景速查

| 场景 | 命令 |
|------|------|
| 改了上一次的 commit message | `git commit --amend` |
| 多个提交压缩成一个 | `git rebase -i HEAD~n` 后标记 squash |
| 撤销已经 push 的提交 | `git revert <commit>` |
| 找回误删的分支 | `git reflog` 找到 commit hash，`git branch <name> <hash>` |
| 暂存区的内容想移到另一个分支 | `git stash` → 切分支 → `git stash pop` |
| 查看某次提交改了什么 | `git show <commit>` |
| 只克隆某个分支 | `git clone -b <branch> --single-branch URL` |
| 修改历史提交的 author | `git rebase -i` → edit → `git commit --amend --author` |

## 总结

Git 命令虽多，但日常工作高频使用的集中在 20 个左右。掌握这些核心命令 + 理解工作区 / 暂存区 / 仓库三棵树的关系，就能应对 90% 的版本控制场景。

**日常最高频 Top 10：**

| 命令 | 用途 |
|------|------|
| `git status` | 查看当前状态 |
| `git add` | 暂存修改 |
| `git commit -m` | 提交修改 |
| `git push` | 推送到远程 |
| `git pull --rebase` | 拉取远程更新 |
| `git checkout -b` | 创建并切换分支 |
| `git merge` | 合并分支 |
| `git log --oneline` | 查看提交历史 |
| `git stash` | 暂存工作区 |
| `git reset` | 撤销操作 |
