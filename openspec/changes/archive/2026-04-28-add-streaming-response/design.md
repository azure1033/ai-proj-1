## Context

当前 `/ask` 使用 `run_agent()` → `agent.invoke()` 同步返回完整结果。用户等待 Agent 完成全部推理后才看到响应。DeepSeek/Claude 等主流 AI 产品的流式输出已成为用户预期——实时展示思考过程和逐字生成。

LangChain 1.x `create_agent` 返回 `CompiledStateGraph`，支持 `.astream()` 和 `.astream_events()` 方法，可以逐事件获取 AI 响应。

## Goals / Non-Goals

**Goals:**
- 后端 SSE 事件：`step`（工具调用开始）→ `step_done`（工具返回）→ `token`（逐字）→ `done`
- 前端实时消费：思考过程面板 + 打字动画 + 自动滚动
- 非流式回退：`stream=false` 保持原 JSON 响应
- Markdown 实时增量渲染

**Non-Goals:**
- 不实现 WebSocket（SSE 足够）
- 不流式传输工具内部输出（只传工具名和最终结果）
- 不修改会话存储逻辑

## Decisions

### Decision 1: 使用 LangChain `astream_events` (v2 API)

**选择**: `agent.astream_events()` 逐事件 yield

```
事件类型:
  on_chat_model_stream → 逐 token
  on_tool_start → 工具调用开始
  on_tool_end → 工具调用结束
```

**备选**: `agent.astream()` 逐节点输出，但粒度不够细（无法拿 token）

### Decision 2: 使用原生 asyncio + StreamingResponse

**选择**: 不引入 `sse-starlette`，用 FastAPI 原生 `StreamingResponse`

```python
from fastapi.responses import StreamingResponse

async def generate_sse(query):
    async for event in run_agent_stream(query):
        yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"

return StreamingResponse(generate_sse(query), media_type="text/event-stream")
```

**理由**: 减少依赖，标准 HTTP SSE 足够。

### Decision 3: 前端使用 fetch + ReadableStream

**选择**: 不用 `EventSource`（不支持 POST），用 `fetch` + `getReader()`

```typescript
const response = await fetch('/ask?stream=true', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query})
})
const reader = response.body.getReader()
const decoder = new TextDecoder()
// 逐行解析 SSE 格式
```

### Decision 4: 思考过程展示

```
┌─ 消息气泡 ──────────────────────────┐
│                                      │
│  🔍 正在搜索: deepseek v4...    ✓   │  ← step 事件
│  📝 正在生成回答...                  │  ← token 流开始
│                                      │
│  DeepSeek V4 于 2025年...           │  ← token 逐字追加
│                                      │
└──────────────────────────────────────┘
```

类似 DeepSeek 的思考过程展示：可展开/折叠，实时更新状态。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| SSE 连接断开 | 前端 `EventSource` 自动重连，或 `fetch` 手动重试 |
| 流式解析错误 | try-catch 包裹每个 chunk，错误时退回非流式 |
| 性能：大量 token 事件 | 前端用 requestAnimationFrame 限流渲染 |
| qwen2.5:3b 不支持 streaming | 降级：一次性返回全部 token，模拟流式输出 |
