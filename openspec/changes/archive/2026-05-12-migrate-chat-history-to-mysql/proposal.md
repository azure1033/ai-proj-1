## Why

当前聊天记录存储采用 Python 内存 dict（`session_memory.py` + `session_manager.py`），服务重启后所有对话历史全部丢失。同时存在遗留的 `chat_history.json` 扁平文件（无 session 隔离，且不参与当前读写流程），导致前端切换会话时无法加载历史消息。迁移到 MySQL 实现持久化存储，并为未来的用户登录系统奠定数据基础。

## What Changes

- **新增** MySQL 8.0 作为持久化存储引擎，替代内存 dict
- **新增** `backend/database.py` — 异步 SQLAlchemy 引擎 + session 工厂
- **新增** `backend/models.py` — ORM 模型（`sessions` 表 + `messages` 表）
- **改造** `backend/session_memory.py` — dict 查询 → MySQL 查询（保持函数签名兼容）
- **改造** `backend/session_manager.py` — dict 查询 → MySQL 查询（保持函数签名兼容）
- **改造** `backend/main.py` — 启动事件初始化数据库，移除 `chat_history.json` 遗留代码
- **新增** docker-compose.yml 中 `mysql` 服务 + 健康检查 + 数据卷
- **新增** `aiomysql`、`cryptography` Python 依赖
- **新增** `.env` 中 `DATABASE_URL`、`MYSQL_*` 环境变量
- **移除** **BREAKING** `chat_history.json` 文件格式（启动时自动迁移至 MySQL "历史记录" 会话）
- 前端 **无变化** — API 接口签名不变

## Capabilities

### New Capabilities
- `chat-history-persistence`: 聊天记录持久化到 MySQL，支持会话隔离、按时间查询、服务重启不丢失

### Modified Capabilities
<!-- 无现有 spec 的需求变更，仅实现细节变化 -->

## Impact

- **Affected code**: `backend/session_memory.py`, `backend/session_manager.py`, `backend/main.py`, `docker-compose.yml`, `.env`
- **New files**: `backend/database.py`, `backend/models.py`, `db/init.sql`
- **New dependencies**: `aiomysql`, `cryptography` (已有 `sqlalchemy==2.0.49` 作为传递依赖)
- **Removed**: `chat_history.json` 读写逻辑（迁移后）
- **Docker**: 新增 mysql 容器，需数据卷 `mysql_data`
- **Breaking**: `chat_history.json` 不再作为存储格式，旧数据一次性迁移至 MySQL
