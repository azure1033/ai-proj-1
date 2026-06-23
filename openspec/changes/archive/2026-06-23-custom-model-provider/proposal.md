## Why

当前 LLM 和 Embedding 模型提供商硬编码在 `model_config.py` 中，用户只能从 3 个预设（智谱/Ollama/SiliconFlow）中选择，且切换需手动修改 `.env` 后重启服务。无法接入 DeepSeek、OpenAI、Groq 等任意 OpenAI 兼容 API，灵活性严重受限。

## What Changes

- **新增** `backend/encryption.py` — Fernet 对称加密，保护 API Key 存储安全
- **新增** `backend/models.py` 中 `ModelProvider` 表 — 持久化存储提供商配置（base_url、api_key 密文、model_name、类型）
- **重写** `backend/model_config.py` → `ModelProviderManager` 类 — 从 DB 动态加载配置，切换即时生效无需重启
- **新增** `backend/main.py` 中 `/providers` CRUD + 激活/测试路由
- **改造** `frontend/SettingsModal.vue` — 预设推荐列表 + 自定义配置表单 + 测试连接按钮
- **新增** LLM 预设：DeepSeek、OpenAI、Groq
- **新增** Embedding 预设：OpenAI Embedding、SiliconFlow Embedding
- **移除** **BREAKING** `.env` 中 `LLM_PROVIDER` / `EMBEDDING_PROVIDER` 等静态配置（改为 DB 驱动），保留 `FERNET_KEY` 用于解密

## Capabilities

### New Capabilities
- `custom-model-provider`: 通过前端 UI 配置任意 OpenAI 兼容的 LLM 和 Embedding 提供商，API Key 加密存储，动态切换无需重启

### Modified Capabilities
- `multi-provider-config`: 提供商配置从 `.env` 静态读取改为 DB 动态加载，切换即时生效（**BREAKING**: 移除 `LLM_PROVIDER` 等环境变量）

## Impact

- **Affected code**: `backend/model_config.py` (重写), `backend/models.py`, `backend/main.py`, `backend/database.py` (新增 preset 初始化), `frontend/SettingsModal.vue`
- **New files**: `backend/encryption.py`
- **New dependencies**: 无（`cryptography` 已安装）
- **Breaking**: `.env` 中 `LLM_PROVIDER`、`EMBEDDING_PROVIDER`、`ZHIPU_API_KEY` 等不再读取（迁移到 DB），仅保留 `FERNET_KEY`
