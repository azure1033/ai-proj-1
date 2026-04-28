## Why

DuckDuckGo 搜索库从 `duckduckgo_search` 更名为 `ddgs`（v8→v9）。旧版本返回空结果，导致 Agent 的 web_search 工具实际上不可用。同时 `session_manager.py` 中 `datetime.utcnow()` 已废弃。

## What Changes

- **`backend/tools/web_search.py`**: import 从 `duckduckgo_search` 改为 `ddgs`
- **`backend/requirements.txt`**: 添加 `ddgs` 依赖
- **`backend/session_manager.py`**: `datetime.utcnow()` → `datetime.now(datetime.UTC)`

## Impact

- 修改 3 个文件，约 5 行
- 需执行 `pip install ddgs`（已完成）
