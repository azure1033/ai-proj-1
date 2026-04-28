## Why

当前系统已实现会话记忆功能，但用户无法在界面上看到和切换不同的会话。当用户想开启新话题或回到之前的对话时，只能通过刷新页面重置，体验不友好。

用户需要一个可视化的会话管理界面：能看到当前有哪些会话、会话名称/预览、能自由切换。

## What Changes

### 前端新增
- **会话列表面板**: 侧边栏或下拉菜单显示所有会话
- **会话切换器**: 点击即可切换到不同会话，加载对应历史
- **会话命名/重命名**: 用户可给会话起有意义的名称
- **会话预览**: 显示会话首条消息/时间，方便识别
- **会话删除**: 可删除不需要的会话

### 后端扩展
- **会话列表 API**: `GET /sessions` 返回用户的会话列表
- **会话重命名 API**: `PATCH /sessions/{id}` 更新会话名称
- **会话删除 API**: `DELETE /sessions/{id}` 删除会话
- **会话持久化**: 当前会话存储在内存中，需要支持会话列表查询

### 数据结构
```typescript
interface Session {
  id: string
  name: string          // 用户自定义名称，默认 "新会话"
  created_at: string    // 创建时间
  updated_at: string    // 最后活动时间
  message_count: number // 消息数量
  preview: string       // 第一条用户消息预览
}
```

## Capabilities

### New Capabilities

- `session-list-ui`: 会话列表 UI - 侧边栏/面板展示所有会话
- `session-switch`: 会话切换 - 点击切换，加载历史消息
- `session-management`: 会话管理 - 重命名、删除会话

### Modified Capabilities

- `session-memory`: 现有会话记忆需要支持会话列表查询和命名

## Impact

- **代码影响**:
  - 新增 `backend/session_manager.py` (会话列表管理)
  - 修改 `backend/main.py` 添加会话管理 API
  - 修改 `frontend/src/components/ChatAssistant.vue` 会话列表 UI
  - 新增 `frontend/src/components/SessionPanel.vue` (可选)
- **依赖影响**: 无新依赖
- **API 影响**: 新增 3 个端点
- **存储影响**: 会话元数据需要持久化（第一阶段用内存）