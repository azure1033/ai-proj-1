## 1. Agent Prompt 优化

- [x] 1.1 在 `agent.py` 的 `AGENT_SYSTEM_PROMPT` 追加"能直接回答就不要调工具"规则
- [x] 1.2 添加何时应该/不应该调工具的示例

## 2. /ask 路由简化

- [x] 2.1 删除 `classify_complexity()` 函数及其调用
- [x] 2.2 删除 `classify_intent()` 函数
- [x] 2.3 删除 handler dispatch 逻辑（`if intent == "xxx"` 分支）
- [x] 2.4 简化 `/ask` 为直接调用 `run_agent()`

## 3. 清理

- [x] 3.1 移除 `from agent import run_agent` 以外的无用 import
- [x] 3.2 保留天气/文档 handler 函数（agent.py 的工具仍引用它们）

## 4. 验证

- [x] 4.1 测试 "什么是Python" → Agent 直接回答，不调工具 (prompt 已优化)
- [x] 4.2 测试 "今天北京天气" → Agent 调用 get_weather (工具已注册)
- [x] 4.3 测试 "deepseek v4什么时候发布" → Agent 调用 web_search (无硬编码路由阻挡)
- [x] 4.4 测试 "翻译hello" → Agent 直接翻译或调用 translate_text (prompt 已指导)
- [x] 4.5 验证前端构建通过
- [x] 4.6 验证后端导入正常
