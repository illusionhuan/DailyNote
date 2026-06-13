---
title: Agent 开发 DAY1：核心概念与术语速查
date: 2026-06-10 10:00:00
tags:
  - Agent
  - LLM
  - AI
  - 人工智能
categories:
  - AI 开发
---

## 前言

Agent（智能体）是当前 AI 应用开发的热门方向。不同于简单的 LLM 对话，Agent 能够自主规划、调用工具、执行多步任务。本文梳理 Agent 开发中最常见的术语和概念，作为系列的第一篇入门笔记。

<!-- more -->

## 核心概念

### LLM（大语言模型）

Large Language Model，Agent 的"大脑"。通过海量文本训练，具备理解和生成自然语言的能力。常见模型：

- **GPT 系列**（OpenAI）— GPT-4o、GPT-4.1
- **Claude 系列**（Anthropic）— Claude Opus、Sonnet、Haiku
- **Gemini 系列**（Google）— Gemini 2.5 Pro
- **开源模型** — Llama、Qwen、DeepSeek

Agent 开发中，LLM 负责理解任务意图、生成执行计划、组织输出结果。

### Agent（智能体）

能够**自主感知环境、做出决策、执行动作**的系统。与普通 LLM 调用的关键区别：

| 特征 | 普通 LLM 调用 | Agent |
|------|--------------|-------|
| 交互方式 | 一问一答 | 多步自主执行 |
| 工具使用 | 不涉及 | 可调用外部工具 |
| 规划能力 | 无 | 自主拆解任务 |
| 记忆 | 仅当前对话 | 短期 + 长期记忆 |

### Tool / Function Calling（工具调用）

Agent 与外部世界交互的手段。通过定义工具的名称、描述和参数，LLM 可以在需要时自动选择并调用：

```python
# 工具定义示例
tools = [
    {
        "name": "search_web",
        "description": "搜索互联网获取最新信息",
        "parameters": {
            "query": {"type": "string", "description": "搜索关键词"}
        }
    },
    {
        "name": "read_file",
        "description": "读取本地文件内容",
        "parameters": {
            "path": {"type": "string", "description": "文件路径"}
        }
    }
]
```

LLM 返回结构化的工具调用指令，由宿主程序执行后将结果回传给 LLM，形成**调用-反馈循环**。

### Prompt（提示词）

与 LLM 交互的输入文本。Agent 开发中常见的 Prompt 类型：

- **System Prompt** — 定义 Agent 的角色、行为规则和可用工具
- **User Prompt** — 用户的自然语言请求
- **Tool Result** — 工具执行后的返回结果

好的 System Prompt 是 Agent 可靠运行的基础。

### Token（令牌）

LLM 处理文本的基本单位。中文大约 1 个字 = 1-2 个 token，英文大约 1 个单词 = 1 个 token。

关键概念：
- **Context Window**（上下文窗口）— 模型单次能处理的最大 token 数，如 128K、200K
- **Input/Output Token** — 输入和输出分别计费，输出通常更贵
- **Token Limit** — 超出窗口限制需要截断或压缩对话历史

### Context Window（上下文窗口）

模型一次能"看到"的全部内容，包含 System Prompt、对话历史、工具结果等。窗口越大，Agent 能参考的信息越多，但成本也越高。

当对话超出窗口时，需要通过**摘要压缩**或**滑动窗口**等策略管理上下文。

## Agent 架构模式

### ReAct（Reasoning + Acting）

最经典的 Agent 架构模式，交替进行**推理**和**行动**：

```
Thought: 用户想知道今天的天气，我需要调用天气工具
Action: search_weather(city="北京")
Observation: 北京今天晴，25°C
Thought: 已经获取到天气信息，可以回复用户
Answer: 北京今天晴天，气温 25°C。
```

这种 Thought → Action → Observation 的循环让 Agent 的决策过程可追踪、可调试。

### Chain of Thought（思维链，CoT）

让 LLM 在给出答案前先展示推理步骤，显著提升复杂任务的准确率：

```
问题：小明有 5 个苹果，给了小红 2 个，又买了 3 个，现在有几个？

思维链：
- 初始：5 个
- 给出 2 个：5 - 2 = 3 个
- 买入 3 个：3 + 3 = 6 个
答案：6 个
```

### Multi-Agent（多智能体）

多个 Agent 协作完成复杂任务。常见协作模式：

- **主从模式** — 一个 Orchestrator 分配任务给多个 Specialist Agent
- **流水线模式** — Agent A 的输出作为 Agent B 的输入
- **讨论模式** — 多个 Agent 互相讨论、辩论，得出结论

### Workflow（工作流）

将 Agent 的执行流程预定义为 DAG（有向无环图），兼顾确定性和灵活性：

```
[用户输入] → [意图识别] → [路由]
                              ├── 简单问题 → [直接回答]
                              └── 复杂问题 → [规划] → [执行] → [验证] → [回答]
```

## 记忆与检索

### Memory（记忆）

Agent 维持上下文和学习能力的机制：

- **短期记忆** — 当前对话的上下文，存在于 Context Window 中
- **长期记忆** — 跨对话持久化的信息，通常存储在数据库中
- **工作记忆** — 当前任务执行过程中的中间状态

### RAG（检索增强生成）

Retrieval-Augmented Generation，在 LLM 生成前先从知识库中检索相关文档，解决 LLM 知识过时和幻觉问题：

```
用户提问 → 向量检索相关文档 → 将文档拼入 Prompt → LLM 基于文档生成回答
```

### Embedding（向量嵌入）

将文本转换为高维向量，使语义相近的文本在向量空间中距离更近。是 RAG 的核心技术：

```python
# 概念示例
vector = embedding_model.encode("Agent 开发入门")
# 输出: [0.023, -0.156, 0.089, ...]  # 维度通常 768~3072
```

### Vector Database（向量数据库）

专门存储和检索向量的数据库，支持高效的相似度搜索：

- **Pinecone** — 云托管，开箱即用
- **Milvus** — 开源，支持大规模部署
- **Chroma** — 轻量级，适合原型开发
- **FAISS**（Meta）— 库而非数据库，适合嵌入已有系统

## 模型相关

### Fine-tuning（微调）

在预训练模型基础上，用特定领域数据继续训练，使模型更适配特定任务。与 Prompt Engineering 的对比：

| 方式 | 成本 | 效果 | 适用场景 |
|------|------|------|---------|
| Prompt Engineering | 低 | 有限 | 快速原型、通用任务 |
| RAG | 中 | 好 | 知识密集型任务 |
| Fine-tuning | 高 | 最好 | 特定风格/格式、领域专精 |

### Hallucination（幻觉）

LLM 生成看似合理但实际错误的内容。Agent 开发中应对策略：

- 使用 RAG 引入可靠知识源
- 要求模型给出信息来源
- 添加事实验证步骤
- 降低 temperature 参数减少随机性

### Temperature（温度）

控制 LLM 输出随机性的参数，范围通常 0~2：

- **0** — 最确定性，每次输出一致，适合代码生成、数据提取
- **0.7** — 平衡创造性和一致性，适合日常对话
- **1.0+** — 更随机、更有创造性，适合头脑风暴

## 总结

以上是 Agent 开发中最核心的术语和概念。理解这些概念后，就能更好地阅读 Agent 框架（如 LangChain、LlamaIndex、CrewAI）的文档，也能更清晰地设计自己的 Agent 系统。

下一篇将动手搭建第一个 Agent，敬请期待。
