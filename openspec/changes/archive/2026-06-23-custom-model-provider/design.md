## Context

当前 `model_config.py` 通过 `.env` 中的 `LLM_PROVIDER` 和 `EMBEDDING_PROVIDER` 静态选择提供商，配置在启动时一次性加载，切换需手动改文件 + 重启。项目已有 MySQL 持久化基础设施（`database.py` + `models.py`），`cryptography` 已安装。

## Goals / Non-Goals

**Goals:**
- 前端 UI 配置任意 OpenAI 兼容的 LLM 和 Embedding 提供商（base_url, api_key, model_name）
- API Key 使用 Fernet 加密存储于 MySQL
- 切换提供商即时生效，无需重启后端
- 提供预设推荐列表（智谱、DeepSeek、OpenAI、Groq、Ollama 等）
- 支持测试连接验证配置有效性
- Embedding 提供商同样可自定义

**Non-Goals:**
- 不改造聊天对话流程（模型切换对 `/ask` 透明）
- 不支持同时使用多个 LLM 提供商（同一时间仅一个激活）
- 不改造 RAG 知识库的 Embedding 下游逻辑

## Decisions

### 1. 动态 Client 创建策略

**选择**: 每次请求动态创建 `openai.OpenAI` / `ChatOpenAI` 实例  
**备选**: 缓存 client 并在 provider 切换时失效  
**理由**: OpenAI client 创建成本极低（仅设置 `api_key` + `base_url` 属性，无网络请求）。每次读取当前激活 provider 的配置创建新实例，天然保证配置实时性，无缓存失效问题。

### 2. API Key 加密方案

**选择**: `cryptography.fernet.Fernet` 对称加密  
**密文流程**: 首次启动自动生成 `FERNET_KEY` → 写入 `.env` → `encryption.py` 加载 → `encrypt()`/`decrypt()`  
**API 响应脱敏**: 仅返回后 4 位（如 `"...xxxx"`），明文仅在 DB 存储和前端输入时出现

### 3. 预设 Provider 初始化

**选择**: `database.py` 的 `init_db()` 中用 `INSERT OR IGNORE` 初始化预设数据  
**预设列表**:

**LLM**:
| id | name | base_url | model_name |
|----|------|----------|------------|
| zhipu | 智谱 AI | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` |
| deepseek | DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| siliconflow | SiliconFlow | `https://api.siliconflow.cn/v1` | `deepseek-ai/DeepSeek-V2.5` |
| openai | OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| groq | Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| ollama | Ollama 本地 | `http://localhost:11434/v1` | `qwen2.5:3b` |

**Embedding**:
| id | name | base_url | model_name |
|----|------|----------|------------|
| zhipu-emb | 智谱 Embedding | `https://open.bigmodel.cn/api/paas/v4` | `embedding-2` |
| openai-emb | OpenAI Embedding | `https://api.openai.com/v1` | `text-embedding-3-small` |
| siliconflow-emb | SiliconFlow Embedding | `https://api.siliconflow.cn/v1` | `BAAI/bge-large-zh-v1.5` |
| local-emb | 本地 text2vec | — | `shibing624/text2vec-base-chinese` |

`local-emb` 是特殊预设：不调用 API，直接使用 HuggingFace 本地模型（与现有逻辑一致）。

### 4. 数据模型

```sql
CREATE TABLE model_providers (
    id          VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,       -- 显示名
    provider_type ENUM('llm', 'embedding') NOT NULL,
    base_url    VARCHAR(500) NOT NULL,
    api_key     VARCHAR(2000) NOT NULL,       -- Fernet 加密后的密文
    model_name  VARCHAR(100) NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT FALSE,
    is_preset   BOOLEAN NOT NULL DEFAULT FALSE, -- 预设不可删
    is_local    BOOLEAN NOT NULL DEFAULT FALSE, -- 本地模型（embedding 专用）
    created_at  DATETIME NOT NULL,
    updated_at  DATETIME NOT NULL
);
```

### 5. 测试连接

`POST /providers/{id}/test` 发送一个最小化请求到 `{base_url}/models`（OpenAI API 的 list models 端点）验证 base_url + api_key 是否有效。成功返回可用模型列表。

### 6. 旧配置迁移

启动时检测 `.env` 中是否存在 `ZHIPU_API_KEY` / `DEEPSEEK_API_KEY` 等旧配置，若存在则自动迁移到对应预设 provider 的 `api_key` 字段（加密后），然后注释掉 `.env` 中的旧配置行。

### 7. model_config.py 保留策略

**选择**: 保留 `model_config.py` 作为同步降级层（非完全移除）  
**理由**: `provider_manager.py` 的缓存未初始化时（DB 未就绪），`_reload_llm_sync()` 回退到 `model_config` 读取 `.env` 配置创建 client。DB 路径（`_reload_llm()`）初始化后覆盖缓存。两层共存保障开发环境（`USE_MYSQL=false`）仍可正常工作。

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| FERNET_KEY 丢失导致已加密 API Key 无法解密 | 提示用户备份 `.env`，Key 丢失后可重新输入 API Key |
| 切换 Embedding provider 后旧向量与新 provider 维度不兼容 | 提示用户需重建知识库索引，提供 "清除并重建" 按钮 |
| 测试连接时请求超时阻塞 UI | 设置 5 秒超时，超时返回明确错误信息 |
| preset 被用户意外修改 | UI 上 preset 的 base_url 和 model_name 字段只读 |

## Open Questions

1. **是否需要支持多个 LLM provider 同时激活？** — 当前设计为单一激活，如未来需要对话中切换模型可扩展。
2. **Embedding provider 切换后旧数据是否需要自动清理？** — 建议提示用户手动操作，避免误删。
