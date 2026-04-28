## Context

`add-agent-mode` 实现了 `WebSearchTool`，支持 Tavily (需 API Key) 和 DuckDuckGo (免费) 两种搜索方案。当前代码存在的问题：
1. 依赖未安装时，错误消息是开发者语言（`pip install xxx`）
2. LLM Agent 无法区分开发者消息和用户消息，直接转发技术细节
3. Tavily 失败后仅返回错误，未尝试 DDG 备选

## Goals / Non-Goals

**Goals:**
- 工具错误消息统一为 `[服务提示: xxx]` 格式，Agent 可识别
- Agent prompt 增加规则：遇到服务提示时转述为用户友好语言
- Tavily 失败时自动 fallback 到 DDG（如果 DDG 可用）

**Non-Goals:**
- 不增加新的搜索方案（不引入 SerpAPI、Bing 等）
- 不修改前端

## Decisions

### Decision 1: 错误消息格式 —— `[服务提示: xxx]` 前缀

**选择**: 所有工具内部错误使用 `[服务提示: xxx]` 前缀

```
之前: "DuckDuckGo 搜索未安装，请运行: pip install duckduckgo-search"
之后: "[服务提示: 搜索服务暂未配置，请基于已有知识回答]"
```

**理由**: LLM 能理解这种 meta 消息，配合 Agent prompt 规则，Agent 会转述为用户语言而非直接展示。

### Decision 2: Agent 提示词规则

在 `AGENT_SYSTEM_PROMPT` 末尾追加降级规则：

```
如果工具返回的消息以 [服务提示:] 开头，说明该功能暂时不可用。
请勿直接向用户展示技术细节。你应该友好告知并基于已有知识提供帮助。
```

### Decision 3: Tavily → DDG 自动降级

Tavily 返回 `[服务提示: ...]` 时，自动尝试 DDG，只有两个都失败才返回服务提示。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| Agent 可能仍会展示技术细节 | Prompt 中明确禁止，实测验证 |
| DDG 搜索结果质量不如 Tavily | 提供 API Key 文档引导用户配置 Tavily |
