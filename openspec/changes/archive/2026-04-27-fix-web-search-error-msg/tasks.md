## 1. 环境依赖

- [x] 1.1 执行 `pip install duckduckgo-search` 安装缺失依赖

## 2. web_search.py 修复

- [x] 2.1 重写 `_search_tavily()` 错误消息为 `[服务提示: xxx]` 前缀格式
- [x] 2.2 重写 `_search_duckduckgo()` 错误消息为 `[服务提示: xxx]` 前缀格式
- [x] 2.3 在 `_run()` 中增加 Tavily 失败 → DDG 自动降级兜底逻辑

## 3. Agent 提示词修复

- [x] 3.1 在 `agent.py` 的 `AGENT_SYSTEM_PROMPT` 追加服务降级规则

## 4. 验证

- [x] 4.1 测试 DDG 搜索可用（安装依赖后）
- [x] 4.2 验证 Agent 遇到服务提示时不再展示 pip install 等开发者消息
