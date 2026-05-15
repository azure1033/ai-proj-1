## 1. 数据库层

- [x] 1.1 在 `backend/models.py` 中新增 `ModelProvider` ORM 模型
- [x] 1.2 在 `db/init.sql` 中新增 `model_providers` 建表语句

## 2. 加解密模块

- [x] 2.1 创建 `backend/encryption.py` — Fernet 加解密工具
- [x] 2.2 在 `backend/database.py` 的 `init_db()` 中：初始化预设 provider 数据（6 个 LLM + 4 个 Embedding preset）

## 3. 模型配置重写

- [x] 3.1 创建 `backend/provider_manager.py` — `ModelProviderManager` 类
- [x] 3.2 更新 `backend/main.py` / `agent.py` 改用 provider_manager
- [x] 3.3 更新 RAG 相关代码（`tools/rag_tool.py`）改用 provider_manager
- [x] 3.4 启动事件增加 `reload_from_db` 调用

## 4. API 路由

- [x] 4.1 `GET /providers` — 列出所有 provider（api_key 脱敏后返回），按 type 分组
- [x] 4.2 `POST /providers` — 新增自定义 provider（api_key 加密后存储）
- [x] 4.3 `PUT /providers/{id}` — 更新 provider 配置（preset 仅允许更新 api_key）
- [x] 4.4 `DELETE /providers/{id}` — 删除自定义 provider（preset 拒绝删除）
- [x] 4.5 `POST /providers/{id}/activate` — 激活指定 provider（同 type 下其他 provider 取消激活）
- [x] 4.6 `POST /providers/{id}/test` — 测试连接，调用 `{base_url}/models`，5 秒超时

## 5. 前端改造

- [x] 5.1 重写 `SettingsModal.vue` 的 LLM 配置区：预设下拉 + "自定义" 选项
- [x] 5.2 重写 Embedding 配置区：同 LLM，预设 + 自定义 + 本地选项
- [x] 5.3 添加 "测试连接" 按钮，调用 `POST /providers/{id}/test`
- [x] 5.4 添加 model_providers API 调用逻辑
- [x] 5.5 api_key 输入框使用 `type="password"`，编辑 preset 时 base_url 和 model_name 只读
- [x] 5.6 移除 "需要重启" 提示文案

## 6. 验证

- [ ] 6.1 Docker 启动，验证 preset 自动创建且 `zhipu` 为默认激活 LLM
- [ ] 6.2 前端添加自定义 provider（如 DeepSeek），测试连接通过
- [ ] 6.3 切换 provider，发送消息验证使用新模型
- [ ] 6.4 验证 api_key 在 DB 中为密文、API 响应中脱敏
- [ ] 6.5 验证删除自定义 provider、无法删除 preset
- [ ] 6.6 验证 Embedding provider 切换后知识库检索正常
