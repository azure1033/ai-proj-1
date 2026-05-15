## 1. 环境与依赖配置

- [x] 1.1 添加 `aiomysql` 和 `cryptography` 到 `backend/requirements.txt`
- [x] 1.2 在 `.env.example` 中添加 `DATABASE_URL`、`MYSQL_ROOT_PASSWORD`、`MYSQL_PASSWORD`、`USE_MYSQL` 配置项及注释
- [x] 1.3 在 `docker-compose.yml` 中添加 `mysql` 服务（镜像 `mysql:8.0`，健康检查，数据卷 `mysql_data`）
- [x] 1.4 在 `docker-compose.yml` 的 `backend` 服务中添加 `depends_on mysql (condition: service_healthy)` 和 `DATABASE_URL` 环境变量
- [x] 1.5 创建 `db/init.sql` 建表脚本（`sessions` 表 + `messages` 表，字符集 utf8mb4）

## 2. 数据库层

- [x] 2.1 创建 `backend/database.py` — 异步 SQLAlchemy 引擎工厂（`create_async_engine`）、`AsyncSession` 工厂、`get_db()` 依赖注入生成器、`init_db()` 建表函数
- [x] 2.2 创建 `backend/models.py` — `SessionModel` ORM 模型（id, name, created_at, updated_at）和 `MessageModel` ORM 模型（id, session_id FK, role, content, intent, steps JSON, created_at），CASCADE 删除
- [x] 2.3 实现 `USE_MYSQL` 环境变量检测逻辑：非 `true` 时回退到内存 dict 模式（database.py 导出 `is_mysql_enabled()`）

## 3. 存储层改造

- [x] 3.1 改造 `backend/session_memory.py` 所有函数，增加 `db: AsyncSession` 参数：`add_message()` → INSERT messages，`get_history()` → SELECT + ORDER BY，`clear_history()` → DELETE，`get_context_window()` → SELECT + LIMIT/OFFSET
- [x] 3.2 改造 `backend/session_manager.py` 所有函数，增加 `db: AsyncSession` 参数：`create_session()` → INSERT sessions，`get_session()` → SELECT + 动态计算 message_count/preview，`list_sessions()` → SELECT + ORDER BY，`update_session()` → UPDATE，`delete_session()` → DELETE（CASCADE），`touch_session()` → UPDATE updated_at
- [x] 3.3 保持所有函数签名向后兼容（仅新增 `db` 参数，返回值格式不变）

## 4. FastAPI 路由改造

- [x] 4.1 在 `backend/main.py` 中添加 `@app.on_event("startup")` 事件：调用 `init_db()` 建表，检测并执行 `chat_history.json` 迁移逻辑
- [x] 4.2 实现 `chat_history.json` → MySQL 迁移逻辑：读取 JSON → 创建 "历史记录" 会话 → 逐条 INSERT 消息 → 重命名为 `.migrated`
- [x] 4.3 更新所有路由函数注入 `db` 依赖（`db: AsyncSession = Depends(get_db)`），传递给 session_memory/session_manager 调用
- [x] 4.4 移除 `backend/main.py` 中 `chat_history.json` 相关遗留代码（`HISTORY_FILE`、`load_history`、`save_history`、`append_history_entry`、`ensure_history_file`、`DELETE /history` 端点）
- [x] 4.5 更新 `docker-compose.yml` 中 backend 的 volumes，移除 `chat_history.json` 挂载

## 5. 验证与收尾

- [ ] 5.1 本地启动 `docker-compose up`，验证 MySQL 健康检查通过、backend 正常启动
- [ ] 5.2 通过 curl 测试 `/ask` 发送消息 → 重启 backend 容器 → 验证 `/sessions/{id}/history` 仍返回消息
- [ ] 5.3 测试 `/sessions` CRUD 全流程（创建、列出、重命名、删除 → CASCADE 删消息）
- [ ] 5.4 测试 `chat_history.json` 存在时的迁移流程（启动 → "历史记录" 会话自动创建 → JSON 被重命名）
- [ ] 5.5 测试 `USE_MYSQL=false` 时回退到内存 dict 模式（开发环境兼容）
- [ ] 5.6 前端联调：切换会话、发送消息、重命名、删除，确认功能正常
