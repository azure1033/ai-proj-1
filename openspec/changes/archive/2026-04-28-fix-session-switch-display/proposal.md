## Why

点击侧边栏的过去会话时，无法正确加载历史消息。根因：前端读取 `res.data.history` 但后端返回 `res.data.messages`。此外存在 initWelcome 闪烁、历史消息丢失 intent、前端元数据不同步等问题。

## What Changes

- **修复 `switchSession()`**: `res.data.history` → `res.data.messages`（关键修复）
- **修复 `initWelcome()` 时机**: 仅在 API 返回空历史时显示欢迎消息，消除闪烁
- **后端 `add_message()` 支持 intent**: Message 结构增加可选 `intent` 字段
- **`switchSession()` 同步元数据**: 加载历史后更新 localStorage 中的 message_count

## Capabilities

### Modified Capabilities

- `session-memory`: Message 结构增加 `intent` 字段；add_message 接口支持 intent 参数
- `session-switch`: switchSession 修复 key 命名 + 优化 UX + 元数据同步

## Impact

- 修改 `backend/session_memory.py` (+5行)
- 修改 `backend/main.py` `/ask` 路由 (+2行)
- 修改 `frontend/.../ChatAssistant.vue` `switchSession()` (+10行)
- **BREAKING**: 无（intent 字段可选，向后兼容）
