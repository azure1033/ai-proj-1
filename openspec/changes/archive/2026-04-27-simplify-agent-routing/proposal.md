## Why

当前系统采用「规则判定 → Agent/快速路径」的双路架构。每次遇到新类型查询，就需要在 `classify_complexity` 中添加硬编码规则。这不仅让代码膨胀，还容易遗漏——用户问"deepseek v4什么时候发布的"就因不在规则中而被误判为普通问答。

Agent 本身就是设计来做这件事的：根据用户输入自主决定调用哪些工具。让 Agent 统一处理所有请求，删除手写路由逻辑。

## What Changes

- **删除 `backend/main.py` 中的 `classify_complexity()` 和 `classify_intent()`** — 约 100 行硬编码规则
- **删除 `backend/main.py` 中的 handler dispatch 逻辑** — `if intent == "xxx"` 分支
- **简化 `/ask` 路由** — 所有请求统一走 Agent
- **优化 Agent prompt** — 加一条规则：能直接回答的不要调用工具

## Capabilities

### Modified Capabilities

- `agent-core`: 路由策略从「规则+Agent」改为「Agent 统一处理」

### Removed Capabilities

无（原有功能由 Agent 工具覆盖）

## Impact

- **代码影响**: 修改 2 个文件（`backend/main.py` 删除 ~120 行、`backend/agent.py` 加 3 行 prompt），净减少 ~115 行
- **依赖影响**: 无
- **API 影响**: 响应始终包含 `steps` 字段（不再区分 Agent/快速路径）
- **兼容性**: 前端已有 `steps` 处理，向后兼容