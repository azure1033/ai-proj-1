## 1. 后端核心 - Session Memory 模块

- [x] 1.1 创建 `backend/session_memory.py` 模块
- [x] 1.2 实现会话存储结构 `Dict[session_id, List[Message]]`
- [x] 1.3 实现 `add_message(session_id, role, content)` 方法
- [x] 1.4 实现 `get_history(session_id)` 方法
- [x] 1.5 实现 `clear_history(session_id)` 方法

## 2. 后端核心 - Context Window 管理

- [x] 2.1 配置 `MAX_MESSAGES=10` 和 `MAX_TOKENS=4000` 常量
- [x] 2.2 实现 `get_context_window(session_id, current_query)` 方法
- [x] 2.3 实现 token 预算控制逻辑（渐进截断最旧消息）
- [x] 2.4 实现 LangChain 消息格式转换 (`HumanMessage`, `AIMessage`)

## 3. 后端 API 扩展

- [x] 3.1 修改 `POST /ask` 接口支持 `session_id` 参数（可选，未传则自动生成）
- [x] 3.2 修改 `POST /ask` 在响应中返回 `session_id`
- [x] 3.3 添加 `GET /history` 端点（查询参数：`session_id`）
- [x] 3.4 添加 `POST /history/clear` 端点（请求体：`session_id`）
- [x] 3.5 添加 `POST /preferences` 端点（保存用户偏好）
- [x] 3.6 添加 `GET /preferences` 端点（查询参数：`session_id`）
- [x] 3.7 修改 `/ask` 路由注入记忆上下文到 LLM prompt

## 4. 前端集成 - ChatAssistant 组件

- [x] 4.1 在 `ChatAssistant.vue` 中生成/管理 `session_id`（使用 `crypto.randomUUID()`）
- [x] 4.2 修改消息列表数据结构，支持存储历史消息
- [x] 4.3 修改 API 调用传递 `session_id` 并从响应中提取
- [x] 4.4 添加"清除历史"按钮 UI
- [x] 4.5 验证前端能正确显示多轮对话上下文

## 5. 偏好记忆功能

- [x] 5.1 在 `session_memory.py` 中添加 `preferences` 存储结构
- [x] 5.2 实现 `set_preference(session_id, key, value)` 方法
- [x] 5.3 实现 `get_preference(session_id, key)` 方法
- [x] 5.4 在 `GET /ask` 响应中注入用户偏好到上下文

## 6. 测试与验证

- [x] 6.1 测试多轮对话上下文保持（用户问"北京天气"→系统回复，再问"明天呢"）
- [x] 6.2 测试上下文窗口限制（超过10条消息时只保留最近10条）
- [x] 6.3 测试 `/history` 和 `/history/clear` 端点
- [x] 6.4 测试 `/preferences` 端点 CRUD 操作
- [x] 6.5 前端多轮对话测试
- [x] 6.6 验证向后兼容（不带 session_id 的请求仍正常工作）