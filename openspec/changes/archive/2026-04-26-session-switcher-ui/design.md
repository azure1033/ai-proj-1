## Context

当前已实现会话记忆功能 (`enhance-context-memory`)，但只有隐式的新会话创建（首次请求自动生成 UUID）。用户无法：
1. 查看有哪些会话
2. 给会话命名
3. 切换到之前的话题
4. 删除不需要的会话

这限制了多会话场景的使用（如工作/生活分开、不同项目分开）。

## Goals / Non-Goals

**Goals:**
- 清晰的会话列表 UI（侧边栏或面板）
- 一键切换会话，加载对应历史
- 会话命名（用户自定义）
- 会话删除
- 会话预览（首条消息、时间）

**Non-Goals:**
- 会话云端同步（本地存储）
- 会话搜索（未来可扩展）
- 多用户/团队协作
- 会话分享

## Decisions

### Decision 1: 前端 UI 布局 —— 左侧会话列表面板

**选择**: 固定左侧面板显示会话列表

```
┌────────────┬─────────────────────────────────┐
│ 会话列表    │         主聊天区域               │
│            │                                 │
│ [+ 新会话]  │   消息1                         │
│ ─────────  │   消息2                         │
│ 会话1 ✓    │   ...                            │
│ 会话2      │                                 │
│ 会话3      │                                 │
│            │                                 │
│ [设置]     │                                 │
└────────────┴─────────────────────────────────┘
```

**替代方案考虑:**
- 下拉菜单: 节省空间但会话多时不便浏览
- 模态框: 需要关闭才能聊天，流程中断
- Tab 页: 占用屏幕空间大，不适合移动端

**结论**: 侧边栏最直观，符合多会话使用习惯

---

### Decision 2: 会话存储 —— 浏览器 localStorage + 后端内存

**选择**: 前端 localStorage 存储会话列表，后端内存存储消息

```
localStorage:
{
  "sessions": [
    { id, name, created_at, updated_at },
    ...
  ],
  "currentSessionId": "xxx"
}
```

**替代方案考虑:**
- 纯后端存储: 需要额外 API 调用，刷新后需重新拉取
- IndexedDB: 更强大但实现复杂，localStorage 足够
- 服务器持久化: 第一阶段太重

**结论**: localStorage 足够实用，刷新后保留会话列表

---

### Decision 3: 会话列表 API 设计

**选择**: RESTful 风格，端点清晰

| 端点 | 方法 | 说明 |
|------|------|------|
| `/sessions` | GET | 列出所有会话 |
| `/sessions/{id}` | PATCH | 更新会话（名称） |
| `/sessions/{id}` | DELETE | 删除会话 |
| `/sessions/{id}/history` | GET | 获取会话历史 |

**替代方案考虑:**
- 嵌套资源: `/sessions/:id/history` 语义清晰
- 扁平设计: `/history?session_id=xxx` 简单但不够 RESTful

**结论**: RESTful 风格，后续扩展性好

---

### Decision 4: 会话元数据结构

**选择**: 轻量元数据 + 动态加载消息

```typescript
interface SessionMeta {
  id: string
  name: string        // 默认 "新会话"
  created_at: string
  updated_at: string
  message_count: number
  preview: string      // 第一条用户消息，前30字符
}
```

**设计考虑:**
- 列表只显示元数据，不加载消息
- 点击切换时调用 `/sessions/:id/history` 加载消息
- 减少数据传输量

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| localStorage 满（5MB）| 限制会话数量（最多50个），自动清理最旧的 |
| 刷新丢失会话列表 | localStorage 持久化，刷新后恢复 |
| 会话名过长 | 限制 20 字符，显示省略 |
| 后端重启丢失 | 明确告知用户（开发阶段限制） |

## Open Questions

1. **Q: 会话超过数量限制如何处理?**
   - 选项 A: 提示用户删除旧会话
   - 选项 B: 自动清理最旧会话
   - **推荐**: 选项 A + 警告提示

2. **Q: 是否需要会话加密?**
   - 第一阶段: 否，纯本地存储
   - 未来: 可用 crypto-js 加密 localStorage