## Context

`session_memory.py`（197 行）管理消息存储和上下文窗口，`session_manager.py`（285 行）管理会话元数据 CRUD。两者互相导入：`session_memory` 在 `add_message` 后调用 `touch_session`（需导入 `session_manager`），`session_manager` 在 `create_session` 后调用 `get_history`（需导入 `session_memory`）。这形成了循环依赖，当前通过 6 处 `try/except ImportError` 守卫勉强工作。

Preview 截取逻辑（`content[:30] + "..."`）在 4 个位置重复：`_build_preview()` 和 `create_session`、`get_session`、`list_sessions` 的 MySQL 路径中。

## Goals / Non-Goals

**Goals:**
- 消除 `session_memory.py` ↔ `session_manager.py` 循环导入
- 统一 preview 截取为单一函数
- 合并 `get_or_create_session` 和 `get_or_create_session_meta`
- 保持所有导出函数签名和返回值格式不变
- `main.py` 只需一处导入

**Non-Goals:**
- 不改变 API 行为或返回值格式
- 不重构双模式（MySQL/内存）分支逻辑
- 不改变数据库模型

## Decisions

### 1. 保留原文件作为兼容别名

```python
# session_memory.py (new)
from session_store import (
    get_or_create_session, add_message, get_history,
    clear_history, get_context_window,
    set_preference, get_preference, get_all_preferences, delete_preferences,
    Message, sessions, preferences,
)
```

```python
# session_manager.py (new)
from session_store import (
    create_session, get_session, list_sessions,
    update_session, delete_session, touch_session,
    get_or_create_session_meta, SessionMeta,
)
```

所有其他导入方（`agent.py`, `tools/` 等）无需修改。仅 `main.py` 改为直接导入 `session_store`。

### 2. 模块内部结构

`session_store.py` 按领域分为三个区块：
1. 类型定义（`Message`, `SessionMeta`）
2. 内存回退存储（`sessions` dict, `preferences` dict, `session_metadata` dict）
3. 公共 API（所有导出函数，保持原有 db 参数模式）

### 3. Preview 统一

```
Before: _build_preview()       ← 内存路径使用
        create_session()       ← MySQL 路径内联
        get_session()          ← MySQL 路径内联
        list_sessions()        ← MySQL 路径内联

After:  _build_preview(messages: list) → str
        ↑ 所有 4 个调用点统一调用
```

### 4. get_or_create_session 合并

Before: 两个函数，`get_or_create_session`（返回 str session_id）和 `get_or_create_session_meta`（返回 tuple）。`main.py` 中 `/ask` 调用前者获取 session_id 传参，`/sessions` 路由调用后者。

After: 保留两个函数签名但实现统一：
```python
async def get_or_create_session(session_id=None, db=None) → str:
    # 内部调用 get_or_create_session_meta → 取 [0]

async def get_or_create_session_meta(session_id=None, db=None) → tuple[str, SessionMeta]:
    # 统一实现，内存和 MySQL 路径
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| 合并后文件 ~350 行，可能被视为过长 | 按领域用注释分隔区块，不引入子模块 |
| 别名文件可能导致混淆 | 添加 docstring 说明 "此文件为兼容别名，请直接导入 session_store" |
| 其他模块可能直接访问 `sessions` 全局 dict | `delete_session` 中访问 `sessions` dict → 改为内部调用 |
