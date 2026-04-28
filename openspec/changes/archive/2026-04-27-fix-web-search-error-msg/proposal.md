## Why

当 `web_search` 工具因依赖未安装而失败时，返回的错误消息是面向开发者的技术语言（如 `pip install duckduckgo-search`），Agent 会原样转发给最终用户，造成糟糕的用户体验。同时工具缺少兜底降级策略。

## What Changes

- **修改 `backend/tools/web_search.py`**: 重写错误消息为 `[服务提示: xxx]` 前缀格式，Agent 可以识别并处理；增加 Tavily→DDG 失败时的兜底逻辑
- **修改 `backend/agent.py`**: Agent 系统提示词增加服务降级规则，遇到 `[服务提示:]` 前缀时友好转述而非直接展示技术细节
- **安装缺失依赖**: `pip install duckduckgo-search`

## Capabilities

### New Capabilities

无（仅修改现有服务降级行为）

### Modified Capabilities

- `agent-tools`: `web_search` 工具的错误消息格式和降级策略变更

## Impact

- **代码影响**: 修改 2 个文件（`backend/tools/web_search.py`, `backend/agent.py`），约 20 行
- **依赖影响**: 需执行 `pip install duckduckgo-search`
- **API 影响**: 无
- **兼容性**: 完全向后兼容
