---
title: Agent 学习 Day4：Function Calling 实战 —— 构建一个能调用工具的 Agent
date: 2026-06-22 10:00:00
tags:
  - Agent
  - Function Calling
  - Claude API
  - AI 开发
categories:
  - AI 开发
---

## 前言

前三篇我们搞清楚了 Agent 是什么（Day 1）、Claude Code 怎么用（Day 2）、学习路线怎么走（Day 3）。从这篇开始进入动手阶段。Function Calling 是 Agent 区别于普通 Chatbot 的核心能力——让 LLM 不再只能"说"，还能"做"。本文用 Claude API 从零构建一个能读写文件、搜索内容、执行命令的文件管理 Agent，跑通完整的工具调用循环。

<!-- more -->

## Function Calling 的工作原理

普通 LLM 调用是单向的：用户提问 → 模型回答。Function Calling 在此基础上加了一个关键环节：**模型可以请求调用外部工具**。

```
用户: "帮我看看 src/ 目录下有哪些 Python 文件"

                    ┌─────────────┐
                    │  LLM 推理    │
                    │ "我需要调用   │
                    │  list_files" │
                    └──────┬──────┘
                           │ tool_use 请求
                           ▼
                    ┌─────────────┐
                    │  宿主程序    │
                    │ 执行工具调用  │
                    └──────┬──────┘
                           │ tool_result
                           ▼
                    ┌─────────────┐
                    │  LLM 推理    │
                    │ "文件列表是   │
                    │  ..."       │
                    └──────┬──────┘
                           │
                           ▼
                    回复用户
```

关键点：**LLM 本身不执行工具**。它只是发出"我想调用某个工具"的请求，实际执行由宿主程序（我们的代码）完成，执行结果再回传给 LLM 继续推理。

## 实战：构建文件管理 Agent

### 第一步：定义工具

工具定义就是告诉 LLM "你有哪些能力可用"。用 JSON Schema 描述每个工具的名称、用途和参数：

```python
tools = [
    {
        "name": "list_files",
        "description": "列出指定目录下的文件和子目录",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "要列出的目录路径，如 './src'"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "read_file",
        "description": "读取指定文件的完整内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径，如 './src/main.py'"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "将内容写入指定文件（会覆盖已有内容）",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "content": {
                    "type": "string",
                    "description": "要写入的内容"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "search_files",
        "description": "在指定目录中搜索包含关键词的文件",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "path": {
                    "type": "string",
                    "description": "搜索目录，默认当前目录"
                }
            },
            "required": ["keyword"]
        }
    }
]
```

**设计原则：**
- **单一职责**：每个工具只做一件事
- **描述清晰**：让 LLM 准确理解什么时候该用哪个工具
- **参数完备**：required 标记必填项，description 说明格式要求

### 第二步：实现工具执行器

工具定义给了 LLM 看，实际执行逻辑写在宿主程序里：

```python
import os
import subprocess

def execute_tool(name: str, input_data: dict) -> str:
    """根据工具名称执行对应逻辑，返回结果字符串"""

    if name == "list_files":
        path = input_data.get("path", ".")
        try:
            entries = os.listdir(path)
            # 标注文件/目录类型
            result = []
            for entry in entries:
                full = os.path.join(path, entry)
                type_tag = "[DIR]" if os.path.isdir(full) else "[FILE]"
                result.append(f"{type_tag} {entry}")
            return "\n".join(result) if result else "(空目录)"
        except FileNotFoundError:
            return f"错误：目录 '{path}' 不存在"

    elif name == "read_file":
        path = input_data["path"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"错误：文件 '{path}' 不存在"
        except Exception as e:
            return f"错误：读取失败 - {e}"

    elif name == "write_file":
        path = input_data["path"]
        content = input_data["content"]
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"成功：已写入 {path}"
        except Exception as e:
            return f"错误：写入失败 - {e}"

    elif name == "search_files":
        keyword = input_data["keyword"]
        path = input_data.get("path", ".")
        matches = []
        for root, dirs, files in os.walk(path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        if keyword in f.read():
                            matches.append(fpath)
                except:
                    pass
        return "\n".join(matches) if matches else f"未找到包含 '{keyword}' 的文件"

    else:
        return f"错误：未知工具 '{name}'"
```

### 第三步：实现调用循环

这是整个 Agent 的核心——一个 `while` 循环，处理 LLM 的工具调用请求，直到 LLM 给出最终回答：

```python
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """你是一个文件管理助手。你可以帮用户查看目录结构、读写文件、搜索内容。
使用提供的工具来完成用户的请求。每次只调用一个工具，根据结果再决定下一步操作。"""

def run_agent(user_message: str, max_turns: int = 10):
    """运行 Agent，支持多轮工具调用"""
    messages = [{"role": "user", "content": user_message}]

    for turn in range(max_turns):
        # 调用 LLM
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        # 检查是否有工具调用
        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if not tool_uses:
            # 没有工具调用，说明 LLM 已经有最终答案
            final_text = [b.text for b in response.content if b.type == "text"]
            return "\n".join(final_text)

        # 有工具调用，逐个执行
        # 先把 LLM 的回复（包含 tool_use）加入消息列表
        messages.append({"role": "assistant", "content": response.content})

        # 执行每个工具调用，收集结果
        tool_results = []
        for tool_use in tool_uses:
            print(f"  🔧 调用工具: {tool_use.name}({tool_use.input})")
            result = execute_tool(tool_use.name, tool_use.input)
            print(f"  ✅ 结果: {result[:100]}...")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            })

        # 将工具结果回传给 LLM
        messages.append({"role": "user", "content": tool_results})

    return "达到最大轮次，停止执行"
```

### 第四步：测试运行

```python
# 测试 1：查看目录结构
print(run_agent("看看当前目录下有哪些文件"))

# 测试 2：多步任务
print(run_agent("在 src/ 目录下搜索包含 'import' 的 Python 文件，然后告诉我搜索结果"))

# 测试 3：写文件
print(run_agent("创建一个 hello.txt，内容为 'Hello from Agent!'"))
```

**运行效果：**

```
> 帮我看看当前目录有哪些文件
  🔧 调用工具: list_files({"path": "."})
  ✅ 结果: [DIR] src
           [DIR] tests
           [FILE] README.md
           [FILE] requirements.txt
当前目录下有 2 个文件夹和 2 个文件：
- src/ 和 tests/ 是目录
- README.md 和 requirements.txt 是文件
```

## 多工具串联：Agent 的真正威力

单个工具调用只是"能做事"，多工具串联才是"能完成任务"。

```
用户: "把 src/utils.py 里的所有函数名列出来"

思考链:
  1. 先读取文件内容 → read_file("src/utils.py")
  2. 从内容中提取函数名 → LLM 自行解析（不需要工具）
  3. 汇总结果回复用户

用户: "搜索项目里所有用了 requests 库的文件，然后列出文件路径"

思考链:
  1. 搜索关键词 → search_files("import requests")
  2. 得到文件列表后直接回复（不需要再调用工具）
```

LLM 会自动决定调用哪些工具、按什么顺序调用、是否需要串联多次调用。这就是 Agent 的"自主规划"能力。

## 进阶：控制工具调用行为

### 强制使用工具（Tool Choice）

```python
# 默认：auto，LLM 自主决定是否调用工具
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    tool_choice={"type": "auto"},  # 默认行为
    messages=messages
)

# 强制调用某个工具（适合需要确保执行的场景）
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    tool_choice={"type": "tool", "name": "list_files"},
    messages=messages
)

# 禁止调用工具（纯文本回复）
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    tool_choice={"type": "none"},
    messages=messages
)
```

### 错误处理与重试

工具调用可能失败，合理的策略是将错误信息返回给 LLM，让它自行调整：

```python
def execute_tool_safe(name: str, input_data: dict) -> str:
    try:
        return execute_tool(name, input_data)
    except Exception as e:
        # 将错误信息返回给 LLM，它会尝试换一种方式
        return f"工具执行失败: {e}。请检查参数是否正确或尝试其他方法。"
```

LLM 收到错误信息后，通常会：
1. 检查参数是否有误
2. 尝试修正后重新调用
3. 或者换一种方式完成任务

## 工具设计的 5 个原则

Day 3 提到了工具设计原则，这里结合实战展开讲：

| 原则 | 说明 | 反例 |
|------|------|------|
| 单一职责 | 一个工具只做一件事 | `file_manager(action, path, content)` — 操作太多，LLM 容易选错 |
| 描述清晰 | description 准确描述工具能力和限制 | `"处理文件"` — 太模糊，LLM 不知道什么时候该用 |
| 参数明确 | 类型、必填、格式都要标注 | 缺少 required 标记 → LLM 可能漏传参数 |
| 错误友好 | 返回有意义的错误信息 | 抛异常 → Agent 崩溃；返回 `"失败"` → LLM 无法诊断 |
| 幂等安全 | 读操作无副作用，写操作可预期 | 重复调用 `write_file` 结果一致，不会产生重复数据 |

## 调试技巧

### 打印完整的请求和响应

```python
# 开启 Anthropic SDK 的日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 常见问题排查

| 症状 | 可能原因 | 解决方案 |
|------|----------|----------|
| LLM 不调用工具 | tool description 不够清晰 | 改进描述，明确使用场景 |
| 调用错误的工具 | 工具之间功能重叠 | 合并或拆分工具，减少歧义 |
| 参数格式错误 | schema 描述不精确 | 在 description 中给出参数示例 |
| 无限循环调用 | 工具返回结果 LLM 无法理解 | 优化返回格式，添加成功/失败标识 |
| 拒绝调用写工具 | 安全限制 | 在 system prompt 中明确授权范围 |

## 完整代码

将以上代码整合为一个可直接运行的 Python 文件：

```python
"""
Agent Day4: Function Calling 实战
一个能读写文件、搜索内容的文件管理 Agent
"""
import os
import anthropic

# ========== 工具定义 ==========
tools = [...]  # 同上文定义

# ========== 工具执行 ==========
def execute_tool(name, input_data):
    ...  # 同上文实现

# ========== Agent 核心循环 ==========
def run_agent(user_message, max_turns=10):
    ...  # 同上文实现

# ========== 启动 ==========
if __name__ == "__main__":
    print("文件管理 Agent 已启动，输入 'quit' 退出\n")
    while True:
        user_input = input("你: ")
        if user_input.lower() in ("quit", "exit", "q"):
            break
        response = run_agent(user_input)
        print(f"\nAgent: {response}\n")
```

完整代码约 120 行，放在 [GitHub 仓库](https://github.com) 中可直接 clone 运行。

## 总结

| 知识点 | 要点 |
|--------|------|
| Function Calling 本质 | LLM 发出调用请求 → 宿主程序执行 → 结果回传 LLM |
| 调用循环 | while 循环处理 tool_use，直到 LLM 返回纯文本 |
| 多工具串联 | LLM 自主决定调用顺序和组合方式 |
| 工具设计 | 单一职责、描述清晰、参数明确、错误友好、幂等安全 |
| 调试 | 打印请求/响应日志，检查 tool description 和 schema |

跑通 Function Calling 后，你就拥有了一个真正"能做事"的 Agent。下一步我们将为 Agent 加上记忆系统，让它能记住对话历史和用户偏好。

**下一篇预告：** Day 5 — 记忆系统，让 Agent 拥有长期记忆。
