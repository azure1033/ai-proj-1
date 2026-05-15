## Context

当前项目使用 Python `dict` 存储所有聊天记录和会话元数据（`session_memory.sessions` + `session_manager.session_metadata`），无任何磁盘持久化。服务重启后数据全部丢失。同时存在遗留的 `chat_history.json` 扁平文件，其存储格式无 session 隔离，且不参与当前的读写流程。

项目已具备 Docker Compose 部署能力（backend + frontend），SQLAlchemy 2.0.49 已作为传递依赖安装。未来规划引入 JWT 用户认证，需要一个可扩展的关系型数据库。

## Goals / Non-Goals

**Goals:**
- 聊天记录和会话元数据在 MySQL 中持久化，服务重启不丢失
- 保持现有 API 接口签名不变（`/ask`, `/sessions`, `/sessions/{id}/history` 等）
- session_memory.py 和 session_manager.py 的函数签名保持兼容（仅内部实现变更）
- Docker Compose 一键启动完整环境（含 MySQL）
- 自动迁移 `chat_history.json` 旧数据到 MySQL

**Non-Goals:**
- 不修改前端代码
- 不引入数据库迁移工具（Alembic）— 本次使用 `create_all()` 建表
- 不引入 ORM repository 层抽象 — 直接在 `session_memory`/`session_manager` 中使用 SQLAlchemy
- 不改造 Agent 工具链（tools/）— 它们不直接依赖存储层

## Decisions

### 1. 异步 SQLAlchemy + aiomysql

**选择**: `sqlalchemy[asyncio]` + `aiomysql` 驱动  
**备选**: 同步 `pymysql`  
**理由**: FastAPI 路由全部为 `async def`，异步数据库调用可避免阻塞事件循环。`aiomysql` 是成熟的纯 Python 异步 MySQL 驱动。未来多用户并发时异步优势更明显。

### 2. 直接在 session_memory/session_manager 中使用 SQLAlchemy

**选择**: 不引入独立的 Repository 层  
**备选**: 创建 `repositories/` 包封装所有 DB 操作  
**理由**: 当前代码规模小（两个模块），直接使用 SQLAlchemy session 已足够清晰。过度抽象增加复杂度。未来如需单元测试 mock，可注入 session 对象。

### 3. 数据库 session 管理: FastAPI dependency + async generator

**选择**: `database.py` 导出 `get_db()` async generator，路由通过 `Depends()` 注入  
**理由**: FastAPI 标准模式，自动处理 session 生命周期（请求进入时创建，返回时关闭）。session_memory/session_manager 函数接收 `AsyncSession` 参数。

### 4. 建表策略: create_all() + 手动 init.sql

**选择**: 同时使用 SQLAlchemy `create_all()`（开发环境）和 `db/init.sql`（Docker 容器启动时执行）  
**理由**: `create_all()` 适合开发迭代，`init.sql` 确保 Docker 部署时表结构与代码一致，不依赖 Python 启动顺序。

### 5. 旧数据迁移: 启动时一次性迁移

**选择**: `main.py` startup event 检测 `chat_history.json`，存在则创建 "历史记录" 会话并将所有消息灌入 MySQL  
**理由**: 简单可靠。旧数据无 session_id，全部归入一个会话是最安全的迁移策略。迁移完成后删除或重命名 JSON 文件避免重复迁移。

### 6. 函数签名: 增加 db 参数，保持向后兼容

**选择**: `session_memory.add_message(db, session_id, role, content, intent)` — 新增 `db` 参数作为第一参数  
**理由**: 明确的依赖注入，调用方（main.py 路由）通过 `Depends(get_db)` 传入 session。不引入全局 db 变量。

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| MySQL 容器启动慢于 backend，导致首次请求失败 | docker-compose `depends_on` + `condition: service_healthy` + backend 重试连接 |
| `aiomysql` 连接池耗尽（当前单用户无此风险） | 配置连接池大小（默认 5 connect + 10 overflow），未来可按需调大 |
| `chat_history.json` 迁移失败阻塞启动 | 迁移逻辑包装在 try/except 中，失败只打印警告不阻止启动 |
| 开发环境无 MySQL 时后端启动失败 | 提供 `.env` 中可选的 `DATABASE_URL`，检测不到则 fallback 到内存 dict（保留降级路径） |
| SQLAlchemy async 会话在同步工具函数中使用不便 | 当前工具函数（tools/）不直接访问数据库，无影响 |

## Open Questions

1. **是否需要保留内存 dict 作为无 MySQL 时的降级方案？** — 建议暂时保留，通过环境变量 `USE_MYSQL=true/false` 切换。MySQL 不可用时回退到内存模式，避免开发环境断连问题。
2. **`.env` 示例是否需要纳入版本控制？** — `.env.example` 应更新 MySQL 相关注释，`.env` 本身已在 `.gitignore`。
