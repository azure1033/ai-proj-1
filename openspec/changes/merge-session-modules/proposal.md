## Why

`session_memory.py` 和 `session_manager.py` 存在循环导入（6 处 `try/except ImportError` 守卫），两者职责高度重叠：preview 截取逻辑在 4 个位置重复实现，`get_or_create_session` 和 `get_or_create_session_meta` 语义模糊。合并为一个模块消除循环依赖、集中会话管理职责。

## What Changes

- **合并** `session_memory.py` + `session_manager.py` → `session_store.py`（~350 行）
- **消除** 6 处 `try/except ImportError` 循环导入守卫
- **统一** 4 处重复的 `content[:30] + "..."` preview 截取 → 1 个 `_build_preview()`
- **合并** `get_or_create_session` + `get_or_create_session_meta` → 单一 `get_or_create_session()`
- **改造** `main.py` 导入：`from session_memory import ...` + `from session_manager import ...` → `from session_store import ...`
- **保留** 原有文件作为兼容别名（`session_memory.py` → `from session_store import *`），避免影响其他导入方
- API 接口不变，返回值格式不变

## Capabilities

### Modified Capabilities
- `chat-history-persistence`: 消息存储和会话元数据管理合并到 `session_store.py`，消除 circular import

## Impact

- **Affected code**: `backend/session_memory.py`, `backend/session_manager.py` → `backend/session_store.py`, `backend/main.py`
- **New files**: `backend/session_store.py`
- **Modified**: `backend/session_memory.py`（兼容别名）, `backend/session_manager.py`（兼容别名）
- **Removed**: 无（保留别名文件）
- **Breaking**: 无 — 导出接口和返回值格式完全兼容
