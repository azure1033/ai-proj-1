# multi-provider-config (delta)

## MODIFIED Requirements

### Requirement: LLM Provider 配置

系统 SHALL 通过 `LLM_PROVIDER` 环境变量或数据库中的活跃 Provider 选择大语言模型服务商。`provider_manager.py` 是获取 LLM 客户端的唯一入口点；`model_config.py` 仅作为 `.env` 配置读取器，在数据库无活跃 Provider 时作为回退。

#### Scenario: 默认使用智谱 LLM

- **WHEN** `LLM_PROVIDER` 未设置或设为 `zhipu`，且数据库无活跃 LLM Provider
- **THEN** 系统通过 `provider_manager.get_active_llm_config()` 获取客户端，内部回退到 `model_config` 的 `glm-4-flash` 配置

#### Scenario: 数据库活跃 Provider 优先

- **WHEN** 数据库中存在 `is_active=true` 的 LLM Provider（如 deepseek）
- **THEN** `provider_manager.get_active_llm_config()` 返回该 Provider 的 `ChatOpenAI` 实例，忽略 `.env` 中的 `LLM_PROVIDER` 设置

#### Scenario: 切换为 Ollama 本地 LLM

- **WHEN** `LLM_PROVIDER=ollama` 且 `OLLAMA_MODEL` 已设置
- **THEN** 系统使用本地 Ollama 服务，模型为 `OLLAMA_MODEL` 指定的模型

#### Scenario: 向后兼容 OLLAMA_MODEL

- **WHEN** `.env` 中设置了 `OLLAMA_MODEL` 但未设置 `LLM_PROVIDER`
- **THEN** 系统自动推断 `LLM_PROVIDER=ollama`，保持向后兼容

### Requirement: Embedding Provider 配置

系统 SHALL 通过 `EMBEDDING_PROVIDER` 环境变量或数据库中的活跃 Embedding Provider 选择嵌入模型服务商。`provider_manager.get_active_embedding()` 是获取 Embedding 实例的唯一入口点。

#### Scenario: 默认使用智谱 Embedding

- **WHEN** `EMBEDDING_PROVIDER` 未设置或设为 `zhipu`，且数据库无活跃 Embedding Provider
- **THEN** 系统通过 `provider_manager.get_active_embedding()` 获取 Embedding 实例，内部回退到 `model_config` 的 `ZhipuAIEmbeddings(model="embedding-2")`

#### Scenario: 数据库活跃 Embedding Provider 优先

- **WHEN** 数据库中存在 `is_active=true` 的 Embedding Provider
- **THEN** `provider_manager.get_active_embedding()` 返回该 Provider 的 Embedding 实例，忽略 `.env` 中的 `EMBEDDING_PROVIDER` 设置

#### Scenario: 切换为本地 Embedding

- **WHEN** `EMBEDDING_PROVIDER=local`
- **THEN** 系统使用 `HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")` 在本地生成嵌入向量

#### Scenario: 智谱 API Key 缺失时本地回退

- **WHEN** `EMBEDDING_PROVIDER=zhipu` 但 `ZHIPU_API_KEY` 未设置
- **THEN** 系统在日志中警告并自动回退到 `local` Provider

### Requirement: Provider 配置独立解耦

系统 SHALL 允许 LLM Provider 和 Embedding Provider 独立选择和组合。

#### Scenario: 混合使用 Ollama LLM + Zhipu Embedding

- **WHEN** `LLM_PROVIDER=ollama` 且 `EMBEDDING_PROVIDER=zhipu`
- **THEN** 对话使用本地 Ollama 模型，文档嵌入使用智谱云端 API，两者互不干扰

### Requirement: model_config.py 降级为纯配置读取器

`model_config.py` SHALL 仅导出配置字典读取函数（`read_llm_config() -> dict`、`read_embedding_config() -> dict`），不再导出客户端实例工厂函数。所有客户端创建由 `provider_manager.py` 统一负责。

#### Scenario: model_config 不再导出客户端

- **WHEN** 执行 `from model_config import get_openai_client`
- **THEN** 导入失败（`ImportError`），因为该函数已被移除

#### Scenario: provider_manager 内部调用 model_config 回退

- **WHEN** `provider_manager._reload_llm_sync()` 被调用且数据库无活跃 Provider
- **THEN** 内部调用 `model_config.read_llm_config()` 获取配置字典，然后自行构建 `ChatOpenAI` 和 `openai.OpenAI` 客户端
