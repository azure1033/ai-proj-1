## 1. 后端 - Message 结构增加 intent

- [x] 1.1 `session_memory.py` 的 `Message` TypedDict 增加 `intent: str | None`
- [x] 1.2 `add_message()` 函数签名增加 `intent: str | None = None` 参数
- [x] 1.3 `main.py` `/ask` 路由调用 `add_message` 时传入 intent

## 2. 前端 - switchSession 修复

- [x] 2.1 `res.data.history` → `res.data.messages` (关键修复!)
- [x] 2.2 移除 `initWelcome()` 调用，改为 API 成功且结果为空时才显示
- [x] 2.3 API 失败时显示欢迎消息作为 fallback + console.error

## 3. 前端 - switchSession 元数据同步

- [x] 3.1 加载历史成功后更新 `sessions` 中当前会话的 `message_count`

## 4. 验证

- [x] 4.1 发送消息后切换到该会话，验证历史正确显示
- [x] 4.2 验证空会话显示欢迎消息
- [x] 4.3 验证历史消息显示 intent 标签
- [x] 4.4 验证前端构建通过
