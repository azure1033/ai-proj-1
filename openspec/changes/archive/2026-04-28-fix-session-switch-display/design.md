## Context

`switchSession(sessionId)` 负责在用户点击侧边栏会话时加载对应的消息历史。当前实现有 4 个问题：

1. 前端读取 `res.data.history`，后端返回 `res.data.messages` → 始终为空
2. `initWelcome()` 在 API 调用前执行 → 历史会话加载时产生闪烁
3. 后端不存 `intent` → 历史消息无意图标签
4. 前端 localStorage 元数据不与后端同步

## Goals / Non-Goals

**Goals:**
- 修复 key 命名，使历史消息能正确显示
- 消除 initWelcome 闪烁
- 历史消息保留 intent 字段
- 切换会话后更新侧边栏计数

**Non-Goals:**
- 不改变 session 存储方案（保持内存 dict）
- 不改变前端侧边栏 UI

## Decisions

### Decision 1: intent 存储为可选字段

```python
class Message(TypedDict):
    role: str
    content: str
    intent: str | None  # 新增，可选
```

不改变现有 `add_message` 调用签名（默认 `None`），向后兼容。

### Decision 2: switchSession UX 优化

```
之前:
  clear → initWelcome → axios → replace

之后:
  clear → axios → success + empty? → initWelcome
               → success + has data? → set messages
               → error → show error
```

### Decision 3: switchSession 后刷新元数据

加载历史成功后，从 `res.data.messages` 的长度更新 localStorage 中当前会话的 `message_count`。

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| 旧消息没有 intent 字段 | 前端 `intent?` 可选，老数据显示正常 |
| /ask 路由调用 add_message 需传 intent | 默认参数 `None`，不改已有调用点 |
