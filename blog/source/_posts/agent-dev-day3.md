---
title: Agent 学习 Day3：从零到一的 Agent 开发学习指南
date: 2026-06-16 10:00:00
tags:
  - Agent
  - AI
  - LLM
  - 学习路线
categories:
  - AI 开发
---

## 前言

Agent 是 AI 应用的下一个范式。它不再是简单的问答机器人，而是能自主规划、调用工具、执行多步骤任务的智能体。本文整理一份系统化的 Agent 学习路线，从基础概念到实战项目，帮助你建立完整的知识体系。

<!-- more -->

## 什么是 Agent

Agent = LLM + 记忆 + 工具调用 + 规划能力

| 组件 | 作用 | 示例 |
|------|------|------|
| LLM | 大脑，负责推理和决策 | Claude、GPT-4、Gemini |
| 记忆 | 存储上下文和历史信息 | 对话历史、向量数据库 |
| 工具 | 与外部世界交互 | 搜索、代码执行、API 调用 |
| 规划 | 分解复杂任务 | 思维链、ReAct、Tree of Thought |

传统 LLM 只能单轮问答，而 Agent 能：
- 将复杂任务拆解为子任务
- 自主决定何时调用什么工具
- 根据执行结果调整策略
- 多轮迭代直到完成目标

## 学习路线图

```
阶段一：基础（1-2 周）
  [LLM 基础] ──▶ [Prompt Engineering] ──▶ [API 调用]
       │                                        │
       └────────────────────────────────────────┘
                         │
                         ▼
阶段二：核心（2-3 周）
  [工具调用 Function Calling] ──▶ [记忆系统] ──▶ [规划策略]
                         │
                         ▼
阶段三：框架（1-2 周）
  [LangChain / LlamaIndex] ──▶ [Claude Agent SDK] ──▶ [AutoGen / CrewAI]
                         │
                         ▼
阶段四：实战（2-4 周）
  [单 Agent 项目] ──▶ [多 Agent 协作] ──▶ [生产级部署]
```

## 阶段一：LLM 基础（1-2 周）

### 1.1 理解 LLM 工作原理

不需要深入数学细节，但需要理解：

- **Transformer 架构**：注意力机制如何让模型理解上下文
- **Token 化**：文本如何被切分为 token，影响成本和上下文长度
- **上下文窗口**：模型能"看到"的信息量限制
- **温度与采样**：如何控制输出的随机性和创造性

**推荐资源**：
- [3Blue1Brown: But what is a GPT?](https://www.youtube.com/watch?v=wjZofJX0v4M) — 可视化讲解 Transformer
- Anthropic 官方文档 — 理解 Claude 的能力边界

### 1.2 Prompt Engineering

Agent 的核心能力来自高质量的 Prompt。必须掌握：

**基础技巧**：
- 角色设定（System Prompt）
- Few-shot 示例
- 思维链（Chain of Thought）
- 结构化输出（JSON Mode）

**进阶技巧**：
- ReAct 模式（Reasoning + Acting）
- 自我反思（Self-Reflection）
- 任务分解（Task Decomposition）

```python
# ReAct 模式示例
system_prompt = """你是一个能使用工具的助手。

可用工具：
- search(query): 搜索信息
- calculate(expression): 数学计算
- write_file(path, content): 写入文件

每次回答时，按以下格式：
Thought: 我需要做什么
Action: 工具名称(参数)
Observation: 工具返回的结果
... (重复直到完成)
Answer: 最终答案
"""
```

### 1.3 API 调用

掌握至少一个 LLM API 的完整用法：

```python
# Claude API 基础调用
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "解释什么是 Agent"}
    ]
)
print(message.content[0].text)
```

**学习要点**：
- 消息格式（system / user / assistant）
- 流式输出（Streaming）
- 错误处理和重试机制
- Token 计数和成本控制

## 阶段二：Agent 核心机制（2-3 周）

### 2.1 工具调用（Function Calling）

这是 Agent 与外部世界交互的核心机制。

```python
# 定义工具
tools = [
    {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如 '北京'"
                }
            },
            "required": ["city"]
        }
    }
]

# 调用 LLM 并传入工具定义
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}]
)

# 处理工具调用
for block in message.content:
    if block.type == "tool_use":
        result = get_weather(**block.input)
        # 将结果返回给 LLM 继续推理
```

**关键概念**：
- 工具定义（JSON Schema）
- 工具选择（LLM 自主决定调用哪个工具）
- 结果回传（将工具执行结果反馈给 LLM）
- 多轮调用（一个任务可能需要多次工具调用）

### 2.2 记忆系统

Agent 的记忆分为三种类型：

| 类型 | 作用 | 实现方式 |
|------|------|----------|
| 短期记忆 | 当前对话上下文 | 消息列表 |
| 长期记忆 | 跨会话的持久信息 | 向量数据库 / 文件 |
| 工作记忆 | 任务执行中的临时状态 | 变量 / Scratchpad |

**向量数据库入门**：

```python
# 使用 ChromaDB 实现简单的长期记忆
import chromadb

client = chromadb.Client()
collection = client.create_collection("agent_memory")

# 存储记忆
collection.add(
    documents=["用户喜欢用 Python 编程", "用户正在学习 Agent 开发"],
    ids=["mem_1", "mem_2"]
)

# 检索相关记忆
results = collection.query(
    query_texts=["用户的编程偏好"],
    n_results=2
)
```

### 2.3 规划策略

Agent 如何分解复杂任务：

**ReAct（Reasoning + Acting）**：
```
Thought: 用户想部署一个网站，我需要先检查环境
Action: bash("node --version")
Observation: v20.10.0
Thought: Node.js 已安装，接下来需要安装依赖
Action: bash("npm install")
Observation: added 150 packages
...
```

**Tree of Thought**：
- 探索多个可能的解决路径
- 评估每条路径的可行性
- 选择最优路径执行

## 阶段三：Agent 框架（1-2 周）

### 3.1 框架对比

| 框架 | 特点 | 适用场景 |
|------|------|----------|
| LangChain | 生态最丰富，组件齐全 | 快速原型开发 |
| LlamaIndex | 专注 RAG 和数据索引 | 知识库问答 |
| Claude Agent SDK | Anthropic 官方，原生支持 | Claude 生态项目 |
| AutoGen | 微软出品，多 Agent 协作 | 复杂工作流 |
| CrewAI | 角色扮演式多 Agent | 团队协作模拟 |

### 3.2 Claude Agent SDK 示例

```python
from anthropic import AnthropicAgent

agent = AnthropicAgent(
    model="claude-sonnet-4-6",
    tools=[search, calculate, write_file],
    system="你是一个研究助手，能搜索信息并生成报告。"
)

result = agent.run("调研 2026 年 AI Agent 的发展趋势，生成一份报告")
```

### 3.3 LangChain 快速入门

```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 初始化模型
llm = ChatAnthropic(model="claude-sonnet-4-6")

# 定义提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# 创建 Agent
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# 运行
result = executor.invoke({"input": "今天北京天气如何？"})
```

## 阶段四：实战项目（2-4 周）

### 4.1 入门项目：个人知识助手

**功能**：
- 读取本地文档（Markdown、PDF）
- 建立向量索引
- 基于文档内容问答

**技术栈**：Claude API + ChromaDB + Python

**学习收获**：RAG 基础、向量检索、文档处理

### 4.2 进阶项目：代码审查 Agent

**功能**：
- 读取 Git diff
- 分析代码变更
- 生成审查意见
- 自动提交评论

**技术栈**：Claude API + GitPython + GitHub API

**学习收获**：工具调用、多步骤推理、API 集成

### 4.3 高级项目：多 Agent 协作系统

**功能**：
- 规划 Agent：分解任务
- 研究 Agent：搜集信息
- 编码 Agent：编写代码
- 审查 Agent：检查质量

**技术栈**：Claude Agent SDK / AutoGen

**学习收获**：多 Agent 通信、任务调度、错误恢复

### 4.4 生产级项目：自动化工作流引擎

**功能**：
- 定义工作流（YAML/DSL）
- Agent 执行各节点
- 状态持久化
- 错误重试和人工介入

**技术栈**：Claude API + Temporal / Prefect + PostgreSQL

**学习收获**：生产级架构、状态管理、可观测性

## 核心技术深入

### Prompt 工程最佳实践

```
# System Prompt 结构
1. 角色定义：你是谁，擅长什么
2. 能力边界：能做什么，不能做什么
3. 输出格式：期望的响应结构
4. 行为准则：遇到不确定时如何处理
5. 示例：Few-shot 示例引导行为
```

### 工具设计原则

1. **单一职责**：每个工具只做一件事
2. **清晰描述**：让 LLM 准确理解工具用途
3. **参数校验**：防止无效输入导致执行失败
4. **错误处理**：返回有意义的错误信息
5. **幂等性**：相同输入产生相同结果

### 安全考虑

- **输入验证**：防止 Prompt 注入
- **权限控制**：限制工具的执行范围
- **沙箱执行**：代码执行在隔离环境中
- **审计日志**：记录所有工具调用
- **人工审批**：高风险操作需要确认

## 学习资源

### 官方文档

- [Anthropic Claude 文档](https://docs.anthropic.com)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [LangChain 文档](https://python.langchain.com)

### 课程

- [DeepLearning.AI: AI Agents in LangGraph](https://www.deeplearning.ai)
- [Anthropic: Prompt Engineering Interactive Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

### 开源项目参考

- [Claude Code](https://github.com/anthropics/claude-code) — Anthropic 官方 Agent
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) — 自主 Agent 先驱
- [OpenDevin](https://github.com/OpenDevin/OpenDevin) — 开发者 Agent

### 社区

- [LangChain Discord](https://discord.gg/langchain)
- [Anthropic Discord](https://discord.gg/anthropic)
- r/LocalLLaMA — 开源 LLM 社区

## 常见陷阱

| 陷阱 | 表现 | 解决方案 |
|------|------|----------|
| 过度依赖框架 | 不理解底层原理 | 先用原生 API 实现，再用框架 |
| 忽略 Prompt 工程 | Agent 行为不稳定 | 投入时间打磨 System Prompt |
| 工具设计不当 | Agent 频繁调用失败 | 遵循单一职责，完善错误处理 |
| 缺少评估体系 | 无法衡量 Agent 质量 | 建立测试用例和评估指标 |
| 安全意识薄弱 | Prompt 注入、权限泄露 | 输入验证 + 权限最小化 |

## 下一步行动

1. **本周**：完成阶段一，掌握 Claude API 调用
2. **下周**：实现一个简单的工具调用 Agent
3. **两周后**：完成个人知识助手项目
4. **一个月后**：尝试多 Agent 协作

关键原则：**边学边做，每学一个概念就写一个可运行的 demo**。

## 总结

Agent 开发的核心能力：

1. **Prompt Engineering** — 让 LLM 按预期行事
2. **工具调用** — 让 Agent 与外部世界交互
3. **记忆系统** — 让 Agent 拥有上下文和历史
4. **规划策略** — 让 Agent 能分解复杂任务

学习顺序建议：先掌握原生 API，再学习框架；先做单 Agent，再做多 Agent；先跑通 demo，再考虑生产化。

下一篇计划深入 Claude Agent SDK 的实际开发，构建一个能读写代码的 Agent。
