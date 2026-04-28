## Context

当前系统使用 `classify_intent(query)` → Handler dispatch 模式。每个意图（天气、问答、总结等）由独立的 `handle_xxx()` 函数处理。系统已有会话记忆（`session_memory.py`）、会话管理（`session_manager.py`）和上下文窗口功能。缺陷：无法处理需要多步推理、多工具协作的复杂查询。

## Goals / Non-Goals

**Goals:**
- Agent 能自主决定调用哪些工具、以什么顺序、何时完成
- 简单查询保持快速路径（不影响性能和延迟）
- 复杂查询自动切换到 Agent 路径
- 前端能展示 Agent 的思考步骤
- 工具集可扩展（新增工具只需注册）
- 向后兼容，现有 API 响应格式不变（新增 `steps` 字段）

**Non-Goals:**
- 不实现 Agent 记忆或长期规划（单次请求内完成）
- 不实现流式输出（P2 流式响应独立实现）
- 不实现多 Agent 协作或 Agent 间通信
- 不替换现有意图分类，Agent 作为补充路径

## Decisions

### Decision 1: Agent 框架 —— LangChain `create_tool_calling_agent`

**选择**: 使用 LangChain 的 `create_tool_calling_agent` + `AgentExecutor`

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=5,
    max_execution_time=30,
    verbose=True,
    handle_parsing_errors=True
)
result = executor.invoke({"input": query, "chat_history": history})
```

**为什么选 Tool-Calling 而非 ReAct:**
- 代码量更少（约 30 行 vs ReAct 的 80+ 行）
- 利用模型原生的 function calling 能力，更可靠
- LangChain 提供 `handle_parsing_errors=True` 自动处理格式错误

**备选方案（模型不支持 tool calling 时）:**
- 回退到自定义 ReAct Loop（手动解析 Thought/Action/Observation）
- 或者切换到支持 tool calling 的模型（DeepSeek API）

**结论**: Tool-Calling Agent 作为首选，自定义 Loop 作为 fallback

---

### Decision 2: Agent 触发策略 —— 渐进式

**选择**: 新增 `classify_complexity(query)` 判断是否需要 Agent

```
/ask 请求
  ├── classify_complexity(query)
  │   ├── 简单意图 → 快速路径 (现有逻辑)
  │   └── 复杂意图 → Agent 路径
  └── 统一响应格式: {intent, response, steps?: [...]}
```

**复杂度判断逻辑:**
```python
def classify_complexity(query: str) -> str:
    # 多地点 / 比较型 / 规划型 / 搜索需求 → agent
    if multi_city(query): return "agent"
    if comparison(query): return "agent"
    if planning(query): return "agent"
    if search_needed(query): return "agent"
    # 其余走原意图分类
    return classify_intent(query)
```

**为什么不用 Agent 处理所有请求:**
- 简单天气查询：Agent loop 至少多 1 次 LLM 调用（延迟 +1000ms）
- 简单翻译/总结：没必要走 tool calling
- 保留快速路径，性能不回退

---

### Decision 3: Tool 设计 —— 从现有 Handler 重构

**选择**: 将现有 `handle_xxx()` 函数封装为 LangChain `BaseTool`

| 原 Handler | Tool 名称 | Tool 描述 |
|-----------|----------|----------|
| `get_weather_advice_with_focus()` | `get_weather` | 获取指定城市的当前天气，返回温度、湿度、天气状况 |
| `handle_summarize()` | `summarize_text` | 总结给定的文本内容 |
| `handle_translate()` | `translate_text` | 将文本翻译成中文 |
| `handle_code_explain()` | `explain_code` | 解释代码逻辑和功能 |
| (新增) | `web_search` | 搜索互联网获取最新信息 |
| (新增) | `calculator` | 执行数学计算 |

**Tool 注册:**
```python
# backend/tools/__init__.py
def get_all_tools() -> list[BaseTool]:
    return [
        WeatherTool(),
        WebSearchTool(),
        SummarizeTool(),
        TranslateTool(),
        ExplainCodeTool(),
        CalculatorTool(),
    ]
```

**Web Search 实现:**
- 首选 Tavily Search API（免费 1000 次/月，中文支持好）
- 备选 DuckDuckGo（免费但中文效果一般）
- 通过环境变量 `TAVILY_API_KEY` 启用

---

### Decision 4: 前端 Agent 步骤展示

**选择**: 在消息对象中新增 `steps` 字段，前端渲染思考链

```typescript
interface Message {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  steps?: AgentStep[]  // 新增
}

interface AgentStep {
  thought: string       // "我需要查询北京的天气"
  tool: string          // "get_weather"
  tool_input: string    // {"city": "北京"}
  observation: string   // "北京晴 25°C..."
}
```

**前端展示:**
```
🤖 正在思考...
  → 查询北京天气         ✓ 25°C 晴
  → 搜索北京户外景点     ✓ 找到 3 个推荐
  → 生成建议...

📝 明天北京晴 25°C，非常适合户外活动！推荐...
```

---

### Decision 5: 后端架构

```
backend/
├── main.py              # classify_complexity, /ask 路由分发
├── agent.py             # Agent 核心: create_agent, run_agent
├── tools/
│   ├── __init__.py      # get_all_tools()
│   ├── weather_tool.py  # 封装 weather_agent
│   ├── web_search.py    # Tavily/DuckDuckGo
│   ├── text_tools.py    # summarize, translate, explain_code
│   └── calculator.py    # 安全计算器
├── weather_agent.py     # 不变（weather_tool 封装它）
├── session_memory.py    # 不变
├── session_manager.py   # 不变
└── model_config.py      # 不变
```

## Risks / Trade-offs

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| qwen2.5:3b 不支持 tool calling | 🔴 高 | 检测模型能力，不支持时回退到自定义 ReAct loop；可切换到 DeepSeek API |
| Agent 循环死循环/超时 | 🟡 中 | `max_iterations=5`, `max_execution_time=30s`, 超时返回部分结果 |
| Tavily API 不可用 | 🟢 低 | 自动降级到 DuckDuckGo Search |
| Agent 响应时间过长 | 🟡 中 | 简单查询走快速路径；前端显示步骤进度缓解等待焦虑 |
| 工具描述与实际行为不符 | 🟢 低 | 工具 description 字段精确描述输入输出格式 |
| eval() 计算器安全风险 | 🟡 中 | 只允许数学表达式，用正则过滤危险操作 |

## Open Questions

- 是否需要支持用户显式触发 Agent（如 `/agent` 命令）？当前设计只支持自动检测
- Agent 步骤是否要保存到会话历史中？当前只在单次请求中返回
