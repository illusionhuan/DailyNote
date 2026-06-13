---
title: Python 异步编程入门指南
date: 2026-06-07 14:00:00
tags:
  - Python
  - 异步编程
  - asyncio
categories:
  - 编程语言
---

## 什么是异步编程？

异步编程是一种编程范式，允许程序在等待 I/O 操作（如网络请求、文件读写）时执行其他任务，而不是阻塞等待。

<!-- more -->

## asyncio 基础

Python 3.4+ 引入了 `asyncio` 模块，提供了编写异步代码的基础：

```python
import asyncio

async def fetch_data(url):
    print(f"开始请求 {url}")
    await asyncio.sleep(1)  # 模拟网络请求
    print(f"完成请求 {url}")
    return {"url": url, "data": "..."}

async def main():
    # 并发执行多个请求
    results = await asyncio.gather(
        fetch_data("https://api.example.com/a"),
        fetch_data("https://api.example.com/b"),
        fetch_data("https://api.example.com/c"),
    )
    return results

asyncio.run(main())
```

## async/await 语法

- `async def` 定义协程函数
- `await` 暂停当前协程，等待异步操作完成
- `asyncio.gather()` 并发运行多个协程

## 实际应用场景

1. **Web 爬虫** - 并发抓取多个页面
2. **API 服务** - 处理大量并发请求
3. **数据处理** - 流式处理大数据集
4. **文件 I/O** - 异步读写文件

## 注意事项

- 异步代码中不要使用阻塞操作（如 `time.sleep()`）
- 使用 `aiohttp` 替代 `requests` 进行异步 HTTP 请求
- 数据库操作使用异步驱动（如 `asyncpg`、`motor`）
