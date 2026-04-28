## Why

当前系统一次性返回完整响应，用户需等待 5-15 秒才能看到任何内容。这在 Agent 模式下尤其明显——用户面对空白屏幕，不知道 AI 在做什么。实现 SSE 流式输出，让用户实时看到 AI 的思考过程和逐字生成的结果，类似 DeepSeek/Claude 的体验。

## What Changes

### 后端
- **新增 `run_agent_stream()`**: LangChain `astream_events` 生成器，逐 token + 步骤流式发出
- **新增 `/ask?stream=true`**: SSE 端点，`event:step` + `event:token` + `event:done`
- **保留 `/ask?stream=false`**: 原 JSON 响应不变

### 前端
- **SSE 消费**: `fetch` + `ReadableStream` 解析 SSE 事件
- **思考过程面板**: 实时展示 Agent 工具调用（"正在搜索..." → "搜索完成 ✓"）
- **打字动画**: token 逐字追加，Markdown 实时渲染
- **自动滚动**: 跟随内容增长平滑滚动

## Capabilities

### New Capabilities

- `streaming-backend`: 后端流式输出 — SSE 协议，Token 级流 + Agent 步骤流
- `streaming-frontend`: 前端流式消费 — 思考过程面板 + 打字动画 + 实时渲染

### Modified Capabilities

- `agent-core`: `run_agent()` 保留，新增 `run_agent_stream()` 流式版本
- `agent-ui`: 消息渲染支持流式追加（非一次性替换）

## Impact

- **代码影响**: 修改 `backend/agent.py` (+40行), `backend/main.py` (+25行), `frontend/.../ChatAssistant.vue` (+80行)
- **依赖影响**: 新增 `sse-starlette`（FastAPI SSE 支持，可选）
- **API 影响**: `/ask` 新增 `stream` 参数，不传时行为不变
- **兼容性**: 完全向后兼容
