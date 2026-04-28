## Why

当前系统采用「意图分类 → 单一 Handler」模式，用户的一次查询只能触发一个固定流程，无法处理需要多步推理、多工具协作的复杂任务（如"比较北京上海天气，推荐更适合旅游的城市"）。引入 Tool-Calling Agent 模式，让系统能自主决定调用哪些工具、按什么顺序、形成最终答案。

## What Changes

- **新增 `backend/agent.py`**: 基于 LangChain `create_tool_calling_agent` 的 Agent 核心，支持多步推理循环
- **新增 `backend/tools/` 目录**: 将现有 handler 重构为可被 Agent 调用的标准 Tool
  - `weather_tool.py` — 封装天气查询为 tool-calling 格式
  - `web_search.py` — 网页搜索工具（Tavily API，备选 DuckDuckGo）
  - `text_tools.py` — 总结/翻译/代码解释作为工具
  - `calculator.py` — 安全计算器
- **修改 `backend/main.py`**: 添加 `classify_complexity()` 判断是否需要 Agent，简单查询保留快速路径
- **修改 `frontend/.../ChatAssistant.vue`**: 显示 Agent 中间步骤（思考 → 工具调用 → 结果）
- 新增环境变量 `TAVILY_API_KEY`（可选，不影响基本功能）

## Capabilities

### New Capabilities

- `agent-core`: Agent 核心 — 基于 tool-calling 的多步推理循环，支持 2-5 步自主决策
- `agent-tools`: Agent 工具集 — weather、web_search、calculator、text_tools 等可组合工具
- `agent-ui`: Agent 界面 — 前端显示思考过程和中间步骤

### Modified Capabilities

无（现有意图分类和快速路径保持不变）

## Impact

- **代码影响**:
  - 新增 `backend/agent.py`
  - 新增 `backend/tools/weather_tool.py`, `web_search.py`, `text_tools.py`, `calculator.py`
  - 修改 `backend/main.py` — 添加 agent 路径，约 50 行
  - 修改 `frontend/src/components/ChatAssistant.vue` — 添加步骤显示
- **依赖影响**: 新增 `tavily-python`（可选）、`duckduckgo-search`（备选）
- **API 影响**: `/ask` 接口新增 `steps` 字段返回 Agent 中间过程，响应格式向后兼容
- **兼容性**: 完全向后兼容，简单查询走原路径不受影响
