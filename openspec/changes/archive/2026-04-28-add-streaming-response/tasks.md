## 1. 后端 - agent.py 流式生成器

- [x] 1.1 实现 `run_agent_stream()` 异步生成器，使用 `agent.astream_events()`
- [x] 1.2 处理 `on_chat_model_stream` → yield token 事件
- [x] 1.3 处理 `on_tool_start` → yield step 事件（含工具名和输入）
- [x] 1.4 处理 `on_tool_end` → yield step_done 事件（含结果摘要）
- [x] 1.5 处理错误 → yield error 事件
- [x] 1.6 保留原有 `run_agent()` 同步版本不变

## 2. 后端 - main.py SSE 端点

- [x] 2.1 `/ask` 增加 `stream` 查询参数（默认 false）
- [x] 2.2 `stream=true` 时调用 `run_agent_stream()` + `StreamingResponse`
- [x] 2.3 SSE 格式: `event: <type>\ndata: <json>\n\n`
- [x] 2.4 `stream=false` 时保持原有 JSON 响应逻辑

## 3. 前端 - SSE 消费

- [x] 3.1 `sendMessage()` 中根据 `stream=true` 分叉为流式/非流式
- [x] 3.2 实现 `fetch` + `ReadableStream` 解析 SSE 事件
- [x] 3.3 处理 `token` 事件：追加文本到当前助手消息
- [x] 3.4 处理 `step` / `step_done` 事件：更新思考面板
- [x] 3.5 处理 `done` 事件：完成消息，保存历史
- [x] 3.6 处理 `error` 事件：显示错误，回退到非流式

## 4. 前端 - 思考过程面板

- [x] 4.1 实现可折叠思考面板 UI（类似 DeepSeek）
- [x] 4.2 step 事件时：显示⏳指示器 + 动画
- [x] 4.3 step_done 事件时：切换为 ✓ + 结果预览
- [x] 4.4 流式完成后自动折叠

## 5. 前端 - 打字动画

- [x] 5.1 实现 CSS 闪烁光标动画 (▊ blinking)
- [x] 5.2 流式期间光标可见，完成后消失
- [x] 5.3 Markdown 增量实时渲染（不完全重渲染）

## 6. 测试与验证

- [x] 6.1 测试 SSE 流式输出（curl 验证 event 格式）
- [x] 6.2 测试非流式回退（原有功能不变）
- [x] 6.3 测试 Agent 步骤流式展示
- [x] 6.4 测试流式错误处理
- [x] 6.5 验证前端构建通过
