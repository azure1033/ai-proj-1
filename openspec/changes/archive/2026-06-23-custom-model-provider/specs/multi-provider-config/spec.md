## MODIFIED Requirements

### Requirement: LLM Provider 配置

系统 SHALL 通过数据库中的 `model_providers` 表选择大语言模型服务商，支持任意 OpenAI 兼容 API 的自定义配置。配置从前端 UI 管理，切换即时生效无需重启。

#### Scenario: 默认使用智谱 LLM
- **WHEN** 系统首次启动且未选择其他活跃 provider
- **THEN** 系统激活 `zhipu` 预设 provider，使用 `glm-4-flash` 模型

#### Scenario: 切换为任意 LLM provider
- **WHEN** 用户通过前端 UI 选择另一个 LLM provider 并保存
- **THEN** 系统立即使用新 provider 的 base_url、api_key、model_name 配置

#### Scenario: 自定义 OpenAI 兼容 provider
- **WHEN** 用户添加自定义 provider（base_url + api_key + model_name）
- **THEN** 系统可使用该 provider 进行对话，前提是 API 符合 OpenAI `/v1/chat/completions` 规范

### Requirement: Embedding Provider 配置

系统 SHALL 通过数据库中的 `model_providers` 表（`provider_type='embedding'`）选择嵌入模型服务商，支持自定义配置和本地模型。

#### Scenario: 默认使用智谱 Embedding
- **WHEN** 系统首次启动且未选择其他活跃 embedding provider
- **THEN** 系统激活 `zhipu-emb` 预设 provider

#### Scenario: 切换为自定义 Embedding provider
- **WHEN** 用户通过前端 UI 选择自定义 Embedding provider
- **THEN** 系统使用该 provider 的 base_url + api_key 创建 OpenAI 兼容的 embeddings 客户端

#### Scenario: 本地 Embedding 特殊处理
- **WHEN** 活跃的 Embedding provider 为 `local-emb`
- **THEN** 系统使用 `HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")` 本地生成嵌入向量，不调用 API

### Requirement: Provider 配置独立解耦

系统 SHALL 允许 LLM Provider 和 Embedding Provider 独立选择和组合，两者配置互不干扰。

#### Scenario: 混合使用不同 LLM 和 Embedding provider
- **WHEN** 用户选择 DeepSeek 作为 LLM provider、OpenAI 作为 Embedding provider
- **THEN** 对话使用 DeepSeek API，文档嵌入使用 OpenAI Embedding API，两者互不干扰

## REMOVED Requirements

### Requirement: 向后兼容 OLLAMA_MODEL
**Reason**: 不再直接读取环境变量配置，改为 DB 驱动
**Migration**: Ollama 作为预设 provider 存在于数据库中，用户需在 UI 中输入 API 地址
