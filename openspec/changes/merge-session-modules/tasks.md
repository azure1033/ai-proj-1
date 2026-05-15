## 1. 合并存储逻辑

- [x] 1.1 创建 `backend/session_store.py`，按领域分为三区块：类型定义、内存回退、公共 API
- [x] 1.2 移植 `session_memory.py` 所有函数
- [x] 1.3 移植 `session_manager.py` 所有函数
- [x] 1.4 统一 `_build_preview()` — 移除 MySQL 路径内联 preview，新增 `_db_session_to_meta()` 统一 DB 查询
- [x] 1.5 合并 `get_or_create_session` 委托给 `get_or_create_session_meta`

## 2. 消除循环导入

- [x] 2.1 移除所有 `try/except ImportError` 守卫 — 单文件无跨模块导入
- [x] 2.2 `delete_session` 直接访问 `sessions` dict 改为内部调用

## 3. 兼容别名

- [x] 3.1 `session_memory.py` → 兼容别名
- [x] 3.2 `session_manager.py` → 兼容别名
- [x] 3.3 别名文件添加 docstring 说明

## 4. 更新调用方

- [x] 4.1 `main.py` 导入合并为单 `from session_store import ...`
- [x] 4.2 其他文件通过别名兼容，无需修改

## 5. 验证

- [ ] 5.1 运行 LSP diagnostics 确认无循环导入警告
- [ ] 5.2 Docker 启动，验证 `/ask` 发送消息 → 切换会话 → 历史消息正常
- [ ] 5.3 验证 `/sessions` CRUD 全流程正常
