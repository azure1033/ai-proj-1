## Context

当前 AI 助手是无状态设计，每次请求独立处理，无法感知会话历史。这导致：
1. 用户无法引用之前的话题（如"刚才说的北京"）
2. 多轮对话体验差，每个问题都需要完整上下文
3. 每次调用都发送完整历史，浪费 token

**当前系统:**
- `POST /ask` 接收单个 query，返回响应
- 无会话标识、无历史存储
- LangChain 作为 LLM 调用层，但未启用 memory

**目标:**
在最小依赖、最快实现的前提下，提供会话级别的上下文感知能力。

## Goals / Non-Goals

**Goals:**
- 实现会话级别的对话历史存储
- 支持用户引用历史对话内容
- 控制注入 LLM 的上下文长度，防止 token 溢出
- 前端可查看当前会话历史
- 向后兼容，不破坏现有 API 契约

**Non-Goals:**
- 用户认证/登录系统
- 跨设备同步（单设备单会话）
- 向量检索/RAG 知识库
- 持久化存储（SQLite/Redis）——第一阶段用内存
- 长期记忆/个性化学习

## Decisions

### Decision 1: 会话管理方案 —— 基于 Session ID 的简单会话隔离

**选择**: 客户端生成 UUID 作为会话 ID，后端用字典存储

```python
# 存储结构
sessions: Dict[str, List[Message]] = {}
# Message = {role: "user"|"assistant", content: str}
```

**替代方案考虑:**
- Cookie-based: 更透明但需要处理 SameSite 策略
- JWT Token: 需要数据库验证，过重
- WebSocket: 支持流式但改造成本高

**结论**: 简单有效，客户端传递 `session_id` 参数即可

---

### Decision 2: 上下文窗口策略 —— 滚动窗口 + Token 预算

**选择**: 最近 N 条消息 + Token 预算双重限制

```python
MAX_MESSAGES = 10  # 最近 10 轮
MAX_TOKENS = 4000  # 约 16000 字符，中文效率低
```

**替代方案考虑:**
- 向量相似度检索: RAG 方向，过重，第一阶段不需要
- 完整历史: token 溢出风险
- 固定 token 截断: 实现复杂，可能截断关键上下文

**结论**: 简单阈值控制足够实用，后续可优化为动态计算

---

### Decision 3: 前端状态管理 —— 会话历史本地存储

**选择**: 前端维护当前会话的消息列表 + 历史标记

```
前端存储:
- messages: 当前会话消息[]
- sessionId: 当前会话UUID
- showHistory: 是否显示历史面板
```

**替代方案考虑:**
- 服务端推送历史: WebSocket 方案，过重
- 每次刷新重新获取: 增加 API 调用
- LocalStorage 持久化: 方便但增加复杂度

**结论**: 内存存储 + UUID 会话标识，刷新后重置（可接受）

---

### Decision 4: 历史注入方式 —— 系统提示 + 对话历史

**选择**: 在 LangChain 的 prompt 中注入历史消息

```python
from langchain.schema import HumanMessage, AIMessage

# 构建带历史的 prompt
messages = [
    SystemMessage(content="你是AI助手..."),
    *history_messages,  # 最近 N 条
    HumanMessage(content=current_query)
]
```

**替代方案考虑:**
- 独立 history endpoint: 需要两次调用
- RAG 检索增强: 过重的架构
- 对话摘要压缩: 需要额外 LLM 调用

**结论**: LangChain 原生支持，最直接

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Token 溢出导致 LLM 报错 | 设置 `MAX_TOKENS` 阈值，超出时截断最旧消息 |
| 内存泄漏（长会话） | `MAX_MESSAGES` 限制，定期清理过期会话 |
| 并发会话冲突 | 每个 session_id 独立存储，互不影响 |
| 前端历史丢失（刷新） | 明确 UX 限制，刷新重置；可选 localStorage |
| 上下文膨胀影响响应速度 | 监控 token 使用，逐步优化截断策略 |

## Open Questions

1. **Q: 会话过期策略?**
   - 当前: 进程存活期间有效，停止后丢失
   - 可选: 添加 TTL 或定时清理（未来持久化后）

2. **Q: 是否需要持久化?**
   - 当前阶段: 否，纯内存
   - 未来: SQLite 或 Redis 按需添加

3. **Q: 是否支持多语言偏好?**
   - 可选功能，`preference-memory` 能力的一部分
   - 第一阶段跳过，保持简单