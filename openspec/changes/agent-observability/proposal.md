## Why

当前项目的"评测闭环"完全依赖手动 Docker 启动 + curl 测试，缺乏结构化指标。每次修改后无法量化的回答以下问题：调用 LLM 花了多少 Token？哪个 Provider 性价比最高？Agent 工具调用链路耗时多少？错误率趋势如何？这些正是 README 强调的"量化成果"思维在运维层面的缺失。

## What Changes

- 新增 `services/observability_service.py`：请求级别的 Token 计数、延迟记录、错误追踪
- 新增数据库表 `request_logs`：每次 `/ask` 调用的结构化日志（session_id, provider, model, tokens_in, tokens_out, latency_ms, error, tool_calls）
- 新增 `GET /metrics` API：返回汇总指标（按 Provider/Model/Tool/时间段分组）
- 新增 `GET /metrics/requests` API：分页查询请求日志
- 前端新增简易 Dashboard：Token 使用趋势图（7 天）、Provider 调用分布饼图、平均延迟趋势线、错误率指标卡
- Agent 工具调用自动注入 trace_id，记录到 `tool_calls` 字段
- 非侵入式：通过 FastAPI middleware 钩子实现，不修改现有路由和服务代码

## Capabilities

### New Capabilities
- `agent-observability`: 请求级监控与指标聚合 — Token 计数、延迟追踪、错误率、Provider 对比、Dashboard 展示

### Modified Capabilities
- 无 — 纯新增功能，不修改现有 API 行为

## Impact

- **后端新增**: `services/observability_service.py`, `models.py` 新增 `RequestLog` ORM, `db/init.sql` 新增表
- **后端新增**: `routers/metrics.py` 提供 `/metrics` 和 `/metrics/requests`
- **前端新增**: `components/Dashboard.tsx` 嵌入 AppSidebar 或独立路由
- **Agent 改动**: `agent.py` 的 `run_agent` 返回结构中新增 `token_usage: {prompt_tokens, completion_tokens}`
- **中间件**: `main.py` 新增 request-level middleware 记录每次 `/ask` 耗时和结果
- **性能影响**: 每次 `/ask` 多一次 DB INSERT（异步，不阻塞响应），聚合查询有索引覆盖
