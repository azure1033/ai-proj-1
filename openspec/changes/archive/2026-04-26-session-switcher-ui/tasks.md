## 1. 后端 - 会话管理 API

- [x] 1.1 创建 `backend/session_manager.py` 模块
- [x] 1.2 实现会话元数据存储结构
- [x] 1.3 实现 `create_session()` 方法
- [x] 1.4 实现 `get_session(id)` 方法
- [x] 1.5 实现 `list_sessions()` 方法
- [x] 1.6 实现 `update_session(id, name)` 方法
- [x] 1.7 实现 `delete_session(id)` 方法
- [x] 1.8 在 `main.py` 添加 `GET /sessions` 端点
- [x] 1.9 在 `main.py` 添加 `PATCH /sessions/{id}` 端点
- [x] 1.10 在 `main.py` 添加 `DELETE /sessions/{id}` 端点
- [x] 1.11 在 `main.py` 添加 `GET /sessions/{id}/history` 端点

## 2. 前端 - 会话列表状态

- [x] 2.1 在 `ChatAssistant.vue` 添加 `sessions` ref (存储会话列表)
- [x] 2.2 实现 `loadSessions()` 从 localStorage 加载会话列表
- [x] 2.3 实现 `saveSessions()` 保存会话列表到 localStorage
- [x] 2.4 添加 `currentSessionId` 持久化到 localStorage
- [x] 2.5 实现 `createNewSession()` 方法
- [x] 2.6 修改 `loadHistory()` 支持指定 session_id

## 3. 前端 - 会话列表 UI 组件

- [x] 3.1 创建 `SessionPanel.vue` 会话列表面板组件
- [x] 3.2 设计会话项布局 (名称、预览、时间)
- [x] 3.3 添加"新会话"按钮
- [x] 3.4 实现当前会话高亮显示
- [x] 3.5 添加滚动和最大高度限制

## 4. 前端 - 会话切换交互

- [x] 4.1 实现 `switchSession(id)` 切换会话方法
- [x] 4.2 切换时调用 API 获取历史并加载消息
- [x] 4.3 更新当前会话 ID 并保存到 localStorage
- [x] 4.4 UI 响应式更新 (高亮变化)

## 5. 前端 - 会话管理交互

- [x] 5.1 添加悬停显示重命名/删除按钮
- [x] 5.2 实现 `renameSession(id)` 重命名功能
- [x] 5.3 实现 `deleteSession(id)` 删除功能
- [x] 5.4 添加删除确认对话框
- [x] 5.5 调用后端 API 完成重命名/删除

## 6. 集成与样式

- [x] 6.1 将 `SessionPanel` 集成到 `ChatAssistant.vue`
- [x] 6.2 设计响应式布局 (移动端收起/展开)
- [x] 6.3 添加 CSS 过渡动画
- [x] 6.4 添加国际化翻译
- [x] 6.5 测试会话切换流畅性