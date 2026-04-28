## Why

当前系统是无状态的——每次对话都是独立的，用户无法引用之前的对话内容。这限制了多轮交互体验（如"刚才说的那个城市"、"继续上次的话题"）。

用户期待更自然的对话体验：记住之前的城市、时间、偏好，提供上下文感知的回复。

## What Changes

### 后端新增
- **会话记忆模块** (`session_memory.py`): 管理对话历史，支持会话级别存储
- **上下文窗口管理**: 智能截取最近 N 轮对话，防止 token 溢出
- **用户偏好存储**: 可选功能，记录用户常查城市、语言偏好等

### 前端增强
- **历史消息展示**: 支持查看当前会话的完整历史
- **上下文指示器**: 显示"基于 X 条历史消息"

### API 新增
- `GET /history`: 获取会话历史
- `POST /history/clear`: 清除当前会话
- `POST /preferences`: 保存用户偏好

### 可选持久化
- 开发阶段：内存存储 (`dict`)
- 生产阶段：SQLite/Redis（按需启用）

## Capabilities

### New Capabilities

- `session-memory`: 会话记忆 - 基于会话 ID 存储对话历史，支持多会话隔离
- `context-window`: 上下文窗口 - 滚动管理历史消息，控制注入 LLM 的上下文长度
- `preference-memory`: 偏好记忆 - 可选功能，记录用户常查城市、语言偏好

### Modified Capabilities

- `chat-assistant`: 现有对话组件需要支持历史消息展示和上下文感知回复

## Impact

- **代码影响**:
  - 新增 `backend/session_memory.py`
  - 修改 `backend/main.py` 添加记忆注入逻辑
  - 修改 `frontend/src/components/ChatAssistant.vue` 显示历史
- **依赖影响**: 暂无新依赖（内存存储），后续可选 SQLite/Redis
- **API 影响**: 新增 3 个端点，响应格式保持一致
- **兼容性**: 向后兼容，不影响现有无状态调用