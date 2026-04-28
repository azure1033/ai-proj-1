## Context

当前架构:

```
/ask
  ├── classify_complexity()  ← 硬编码规则 (60行)
  │   ├── 多城市 → agent
  │   ├── 比较型 → agent
  │   ├── 规划型 → agent
  │   ├── 搜索 → agent
  │   ├── 人物+时间 → agent
  │   └── 事件问句 → agent
  │
  ├── 命中? → Agent 路径 → run_agent()
  └── 未命中? → classify_intent() → handlers (50行)
```

问题: 每次遇到新类型查询就需要在 `classify_complexity` 加规则。Agent 本身已经能自主决策，不需要上层硬编码路由。

## Goals / Non-Goals

**Goals:**
- 删除全部手写路由规则
- 所有请求统一走 Agent
- 简单查询延迟增加 < 1 秒（Agent 应该直接回答不调工具）
- 误判问题彻底消除

**Non-Goals:**
- 不删除工具实现（weather_tool, web_search 等保留）
- 不删除 session 管理逻辑
- 不修改前端

## Decisions

### Decision 1: 统一 Agent 路由

**选择**: 删除 `classify_complexity` 和 `classify_intent`，所有 `/ask` 请求直接调用 `run_agent()`

```
之前: /ask → classify_complexity (60行) → classify_intent (50行) → handlers (50行) or run_agent
之后: /ask → run_agent
```

**Agent prompt 关键规则**:

```
如果用户的问题你可以基于训练知识直接回答，请直接回答而不要调用工具。
例如:
- "什么是Python" → 直接回答
- "翻译hello" → 直接翻译（或调用 translate_text）
- "今天天气如何" → 调用 get_weather

优先使用简洁直接的方式，只在确实需要工具时再调用。
```

**为什么可行**: Agent 收到 "deepseek v4什么时候发布的" 时，它知道自己知识截止日期，会自动判断需要 `web_search` 来获取最新信息。不需要外部规则告诉它。

**延迟权衡**:
- 简单查询: 之前 1 次 LLM 调用 → 之后 1 次 LLM 调用（Agent 看到 query 直接回答，不调工具）
- 复杂查询: 之前 2+N 次 → 之后 2+N 次（不变）
- 偶尔多 1 次调用: Agent 可能先做一次无工具思考，但这是合理代价

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| Agent 对简单问题也调用工具 | Prompt 明确指示"能直接回答就不要调用工具" |
| 天气查询多一次 Agent 决策调用 | 实测，如果延迟不可接受可加天气关键词快速 bypass |
| qwen2.5:3b 可能不遵循 prompt | 实测，不行就保留最简单的一层天气检测作为性能优化 |

## Migration Plan

1. 修改 Agent prompt
2. 简化 `/ask` 为直接调用 Agent
3. 注释 classify_complexity/classify_intent（保留以备 revert）
4. 测试后删除注释代码
