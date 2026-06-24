## Context

项目 README 强调"量化成果"和"评测闭环"，但当前 DevOps 层面缺少结构化监控。每次 LLM 调用花费的 Token 和时间无法追踪，Provider 性价比不可比，错误趋势不可见。这是一个纯新增特性，不影响现有功能。

## Goals / Non-Goals

**Goals:**
1. 每次 `/ask` 请求自动记录：session_id, provider, model, tokens_in, tokens_out, latency_ms, error, tool_calls
2. 提供聚合查询 API：按 Provider/Model/Tool/时间维度汇总
3. 前端 Dashboard 展示基础指标卡 + 趋势图

**Non-Goals:**
- 不修改现有 API 行为（纯旁路记录）
- 不做实时告警（PagerDuty/Slack 集成）
- 不做成本计费计算（预算管理）
- 不记录对话内容（隐私保护 — 仅元数据）

## Decisions

### D1: 非侵入式中件间模式

**Decision:** 通过 FastAPI middleware 钩子实现记录，不修改任何现有的 router/service 代码。

```python
# main.py
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    if request.url.path == "/ask" and request.method == "POST":
        # 异步写入 DB，不阻塞响应
        asyncio.create_task(save_request_log(...))
    return response
```

**Rationale:** 零侵入，不影响现有代码。Middleware 在响应返回后异步写 DB，对用户感知延迟为零。

### D2: 结构化日志表设计

```sql
CREATE TABLE request_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    provider_id VARCHAR(50),
    model_name VARCHAR(100),
    tokens_in INT DEFAULT 0,
    tokens_out INT DEFAULT 0,
    latency_ms INT DEFAULT 0,
    tool_calls INT DEFAULT 0,
    tool_names JSON,
    error VARCHAR(500),
    created_at DATETIME DEFAULT NOW(),
    INDEX idx_session (session_id),
    INDEX idx_provider (provider_id),
    INDEX idx_created (created_at)
);
```

### D3: Agent Token 提取

LangChain 的 `invoke()` 返回的 messages 中最后一条 AIMessage 通常包含 `response_metadata` 中的 `token_usage`。需要在 `agent.py` 的 `run_agent()` 中解析并返回。

```python
# agent.py run_agent() 返回值新增字段
return {
    "response": ...,
    "steps": ...,
    "token_usage": {"prompt_tokens": N, "completion_tokens": N}  # NEW
}
```

### D4: 前端 Dashboard 设计

指标卡 + 简单趋势，不引入图表库（保持零依赖原则）。用纯 CSS/SVG 画简单图表：

- **指标卡**：今日 Token 总量、平均延迟、错误率、调用次数
- **Provider 分布**：CSS bar chart（各 Provider 的 Token 占比）
- **7 天趋势**：简易 SVG line chart

### D5: 指标 API 设计

```
GET /metrics?days=7  → {
    total_requests, total_tokens, avg_latency_ms, error_rate,
    by_provider: [{provider_id, count, tokens, avg_latency}],
    by_model: [...],
    daily: [{date, count, tokens}]
}

GET /metrics/requests?page=1&limit=20  → {
    items: [{id, session_id, provider, model, tokens_in, tokens_out, latency_ms, error, created_at}],
    total, page
}
```

## Risks / Trade-offs

- **[Risk] DB 写入量随请求量线性增长** → 按月归档老数据，`request_logs` 表保留最近 90 天
- **[Risk] Agent token_usage 字段 LangChain 不同 Provider 返回格式不一致** → 添加 try/except 回退，提取失败时 tokens_in/out 填 0
- **[Trade-off] Middleware 异步写入可能在服务崩溃时丢失最后一条记录** → 可接受。监控数据允许少量丢失，不影响核心对话功能
- **[Trade-off] Dashboard 不用图表库导致图表简陋** → 可接受。保持零依赖，后续可引入轻量 chart 库

## Open Questions

1. **是否需要记录对话内容摘要？** — 不。隐私优先，仅记录元数据。
2. **是否需要按用户区分？** — 暂无用户系统，所有请求归入全局统计。
3. **Dashboard 放在哪里？** — AppSidebar 新增 "Dashboard" 按钮，点击切换 ChatView 为 Dashboard 视图。
