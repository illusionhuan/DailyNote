---
title: "Linux常用命令：从入门到实战速查手册"
date: 2026-06-28 16:00:00
tags:
  - Linux
  - 运维
  - 命令行
categories:
  - 运维与工具
---

## 前言

不管你是后端开发、前端部署还是运维工程师，Linux 命令行都是绕不开的技能。本文按使用场景分类，系统梳理日常开发中最常用的 Linux 命令，每个命令附带实际用法和常用参数，适合作为速查手册随时翻阅。

<!-- more -->

## 一、文件与目录操作

### 1.1 目录导航

```bash
pwd                        # 显示当前目录路径
cd /home/user              # 切换到绝对路径
cd ..                      # 返回上一级
cd ~                       # 回到用户主目录
cd -                       # 回到上一次所在的目录
```

### 1.2 查看目录内容

```bash
ls                         # 列出当前目录文件
ls -l                      # 详细列表（权限、大小、时间）
ls -la                     # 包含隐藏文件（以 . 开头的文件）
ls -lh                     # 文件大小显示为 KB/MB
ls -lt                     # 按修改时间排序（最新的在前）
ls -ltr                    # 按修改时间倒序（最早的在前）
```

`ls -l` 输出解读：

```
drwxr-xr-x  2 user group 4096 Jun 28 10:00 docs
-rw-r--r--  1 user group 1234 Jun 28 09:00 readme.md
│├─┤├─┤├─┤  │  │    │    │    │          │
│ │   │  │  硬链接 属主 组  大小 修改时间  文件名
│ │   │  其他用户权限
│ │   同组用户权限
│ 文件属主权限
文件类型（d=目录, -=普通文件, l=链接）
```

### 1.3 创建与删除

```bash
# 创建
mkdir dir1                 # 创建目录
mkdir -p a/b/c             # 递归创建多层目录
touch file.txt             # 创建空文件（或更新时间戳）

# 删除
rm file.txt                # 删除文件
rm -r dir1                 # 递归删除目录及其内容
rm -rf dir1                # 强制递归删除（不提示确认，慎用！）
rmdir dir1                 # 删除空目录
```

### 1.4 复制与移动

```bash
cp file1 file2             # 复制文件
cp -r dir1 dir2            # 递归复制目录
cp -i file1 file2          # 覆盖前提示确认

mv file1 file2             # 重命名
mv file1 /tmp/             # 移动文件
mv -i file1 /tmp/          # 覆盖前提示确认
```

### 1.5 查找文件

```bash
# find：按条件查找
find /home -name "*.log"              # 按文件名查找
find . -type f -name "*.ts"           # 只找文件
find . -type d -name "node_modules"   # 只找目录
find . -size +100M                    # 找大于 100MB 的文件
find . -mtime -7                      # 找 7 天内修改过的文件
find . -name "*.log" -delete          # 找到并删除

# locate：基于索引的快速查找（需先 updatedb）
locate nginx.conf
```

## 二、文件内容查看与编辑

### 2.1 查看文件内容

```bash
cat file.txt               # 显示整个文件
cat -n file.txt            # 带行号显示
head file.txt              # 显示前 10 行
head -n 20 file.txt        # 显示前 20 行
tail file.txt              # 显示末尾 10 行
tail -n 20 file.txt        # 显示末尾 20 行
tail -f log.txt            # 实时追踪文件末尾（看日志神器）
less file.txt              # 分页浏览（q 退出，/ 搜索，n 下一个）
more file.txt              # 分页浏览（只能向下翻）
wc -l file.txt             # 统计行数
wc -w file.txt             # 统计单词数
```

### 2.2 文本处理三剑客

#### grep：搜索文本

```bash
grep "error" log.txt                   # 搜索包含 error 的行
grep -i "error" log.txt                # 忽略大小写
grep -n "error" log.txt                # 显示行号
grep -r "TODO" ./src                   # 递归搜索目录
grep -c "error" log.txt                # 统计匹配行数
grep -v "debug" log.txt                # 反向匹配（排除 debug 行）
grep -E "error|warn" log.txt           # 正则匹配（多个关键词）
grep -A 3 "error" log.txt              # 显示匹配行及后 3 行
grep -B 3 "error" log.txt              # 显示匹配行及前 3 行
```

#### sed：流编辑器

```bash
sed 's/old/new/' file.txt              # 替换每行第一个匹配
sed 's/old/new/g' file.txt             # 替换所有匹配
sed -i 's/old/new/g' file.txt          # 直接修改文件（-i 原地编辑）
sed -i.bak 's/old/new/g' file.txt      # 修改前备份为 .bak
sed -n '10,20p' file.txt               # 只显示第 10-20 行
sed '3d' file.txt                      # 删除第 3 行
sed '/^$/d' file.txt                   # 删除空行
```

#### awk：文本分析

```bash
awk '{print $1}' file.txt              # 打印每行第 1 列
awk '{print $1, $3}' file.txt          # 打印第 1 和第 3 列
awk -F: '{print $1}' /etc/passwd       # 指定分隔符为 :
awk '$3 > 100' file.txt                # 过滤第 3 列大于 100 的行
awk '{sum += $1} END {print sum}' file.txt  # 求和
awk 'NR >= 10 && NR <= 20' file.txt    # 打印第 10-20 行
```

### 2.3 管道与重定向

```bash
# 管道：前一个命令的输出作为下一个命令的输入
ps aux | grep nginx | grep -v grep

# 重定向
echo "hello" > file.txt          # 覆盖写入
echo "world" >> file.txt         # 追加写入
command 2> error.log             # 错误输出重定向
command > out.txt 2>&1           # 标准输出和错误都重定向
command &> all.log               # 同上（简写）
cat << EOF > config.txt          # Here Document
server {
  listen 80;
}
EOF
```

## 三、权限管理

### 3.1 权限表示

```
rwxrwxrwx
│││││││││
││││││└─┘ 其他用户（r=4, w=2, x=1）
││││││
│││└───┘ 同组用户
│││
│└────── 文件属主

755 = rwxr-xr-x（属主全部权限，组和其他用户读+执行）
644 = rw-r--r--（属主读写，其他只读）
```

### 3.2 修改权限

```bash
chmod 755 script.sh            # 数字模式
chmod u+x script.sh            # 给属主加执行权限
chmod g-w file.txt             # 去掉组的写权限
chmod o+r file.txt             # 给其他用户加读权限
chmod a+x script.sh            # 所有人加执行权限
chmod -R 755 ./dir             # 递归修改目录权限
```

### 3.3 修改所有者

```bash
chown user:group file.txt      # 修改属主和组
chown -R user:group ./dir      # 递归修改
chgrp group file.txt           # 只修改组
```

## 四、用户管理

```bash
whoami                       # 显示当前用户名
id                           # 显示用户 ID 和组信息
sudo command                 # 以 root 权限执行命令

useradd -m newuser           # 创建用户（-m 创建主目录）
passwd newuser               # 设置密码
userdel -r newuser           # 删除用户（-r 同时删除主目录）

groupadd devgroup            # 创建用户组
usermod -aG devgroup user    # 将用户添加到组（-a 追加）
groups user                  # 查看用户所属的组

su - user                    # 切换用户
sudo -u user command         # 以指定用户身份执行命令
```

## 五、进程管理

### 5.1 查看进程

```bash
ps aux                       # 查看所有进程（BSD 风格）
ps -ef                       # 查看所有进程（System V 风格）
ps aux | grep nginx          # 查找特定进程
top                          # 实时查看进程（按 q 退出）
htop                         # 增强版 top（需安装）
```

`ps aux` 输出关键列：

| 列 | 含义 |
|----|------|
| USER | 进程属主 |
| PID | 进程 ID |
| %CPU | CPU 占用率 |
| %MEM | 内存占用率 |
| COMMAND | 启动命令 |

### 5.2 控制进程

```bash
kill PID                     # 发送 SIGTERM（优雅终止）
kill -9 PID                  # 发送 SIGKILL（强制终止）
killall nginx                # 按进程名杀掉所有同名进程
pkill -f "node server"       # 按命令行模式杀进程

nohup ./app &                # 后台运行，终端关闭不会被杀
./app &                      # 后台运行（终端关闭会被杀）
jobs                         # 查看当前终端的后台任务
fg %1                        # 将后台任务调到前台
bg %1                        # 让暂停的任务在后台继续运行
```

### 5.3 系统资源

```bash
free -h                      # 查看内存使用（-h 人类可读格式）
df -h                        # 查看磁盘使用
du -sh ./dir                 # 查看目录大小
du -sh * | sort -rh | head   # 当前目录下最大的 10 个文件/目录
uptime                       # 系统运行时间和负载
vmstat 1 5                   # 每秒采样 5 次系统状态
```

## 六、网络命令

### 6.1 网络连接与测试

```bash
ping google.com              # 测试网络连通性
curl https://api.example.com # 发送 HTTP 请求
curl -o file.zip URL         # 下载文件
curl -X POST -d '{}' URL    # POST 请求
wget URL                     # 下载文件
wget -c URL                  # 断点续传
```

### 6.2 端口与连接

```bash
netstat -tlnp                # 查看监听端口（推荐）
ss -tlnp                     # 同上（更现代的替代）
lsof -i :80                  # 查看占用 80 端口的进程
lsof -i -P -n                # 查看所有网络连接
```

### 6.3 远程操作

```bash
ssh user@host                # SSH 连接远程服务器
ssh -p 2222 user@host        # 指定端口
scp file.txt user@host:/tmp/ # 上传文件
scp -r ./dir user@host:/tmp/ # 上传目录
scp user@host:/tmp/file .    # 下载文件
rsync -avz ./dir user@host:/tmp/  # 增量同步（比 scp 高效）
```

## 七、压缩与解压

```bash
# tar（最常用）
tar -czf archive.tar.gz ./dir       # 压缩目录为 .tar.gz
tar -xzf archive.tar.gz             # 解压 .tar.gz
tar -xzf archive.tar.gz -C /tmp/   # 解压到指定目录
tar -tjf archive.tar.bz2            # 查看 .tar.bz2 内容
tar -xjf archive.tar.bz2            # 解压 .tar.bz2

# 常用参数记忆
# c = create（创建）
# x = extract（解压）
# z = gzip
# j = bzip2
# f = file（指定文件名）
# v = verbose（显示过程）

# zip
zip -r archive.zip ./dir            # 压缩目录
unzip archive.zip                    # 解压
unzip archive.zip -d /tmp/          # 解压到指定目录

# gzip
gzip file.txt                        # 压缩（原文件被替换为 .gz）
gunzip file.txt.gz                   # 解压
```

## 八、系统信息

```bash
uname -a                           # 内核版本信息
cat /etc/os-release                 # 发行版信息
hostname                           # 主机名
date                               # 当前日期时间
cal                                # 日历
history                            # 命令历史
!100                               # 执行历史中第 100 条命令
!!                                 # 执行上一条命令
```

## 九、实用技巧

### 9.1 命令别名

```bash
alias ll='ls -la'
alias gs='git status'
alias dc='docker compose'
unalias ll
```

持久化：写入 `~/.bashrc` 或 `~/.zshrc`。

### 9.2 后台任务管理

```bash
# tmux：终端复用器（推荐）
tmux new -s mysession              # 创建会话
tmux attach -t mysession           # 重新连接
# 快捷键：Ctrl+B, D 分离会话

# screen（传统方案）
screen -S mysession
screen -r mysession
```

### 9.3 定时任务

```bash
crontab -e                         # 编辑定时任务
crontab -l                         # 查看当前任务

# 格式：分 时 日 月 周 命令
# 每天凌晨 3 点执行
0 3 * * * /home/user/backup.sh

# 每 5 分钟执行
*/5 * * * * /home/user/check.sh

# 每周一上午 9 点
0 9 * * 1 /home/user/report.sh
```

### 9.4 快捷键

| 快捷键 | 作用 |
|--------|------|
| `Ctrl + C` | 终止当前命令 |
| `Ctrl + Z` | 暂停当前命令（`bg` 恢复） |
| `Ctrl + A` | 光标移到行首 |
| `Ctrl + E` | 光标移到行末 |
| `Ctrl + R` | 搜索历史命令 |
| `Ctrl + L` | 清屏 |
| `Tab` | 自动补全 |
| `!!` | 重复上一条命令 |
| `sudo !!` | 以 root 权限重复上一条命令 |

## 总结

Linux 命令的核心是**组合**——单个命令能力有限，通过管道 `|` 和重定向 `>` 把它们串起来才是真正的威力。记住最常用的 20 个命令，遇到不熟的随时 `man command` 或 `command --help` 查看手册。

**日常最高频 Top 10：**

| 命令 | 用途 |
|------|------|
| `ls -la` | 查看目录内容 |
| `cd` | 切换目录 |
| `grep` | 搜索文本 |
| `find` | 查找文件 |
| `tail -f` | 实时看日志 |
| `chmod` | 改权限 |
| `ps aux` | 查看进程 |
| `kill` | 杀进程 |
| `curl` | HTTP 请求 |
| `ssh` | 远程连接 |
