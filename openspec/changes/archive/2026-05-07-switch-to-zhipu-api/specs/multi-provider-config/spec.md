## ADDED Requirements

### Requirement: LLM Provider 配置

系统 SHALL 通过 `LLM_PROVIDER` 环境变量选择大语言模型服务商，支持 `zhipu`（默认）、`ollama`、`siliconflow` 三种 Provider。

#### Scenario: 默认使用智谱 LLM

- **WHEN** `LLM_PROVIDER` 未设置或设为 `zhipu`
- **THEN** 系统使用智谱 AI 的 `glm-4-flash` 模型，通过 `ChatOpenAI` 以 OpenAI 兼容模式连接 `https://open.bigmodel.cn/api/paas/v4/`

#### Scenario: 切换为 Ollama 本地 LLM

- **WHEN** `LLM_PROVIDER=ollama` 且 `OLLAMA_MODEL` 已设置
- **THEN** 系统使用本地 Ollama 服务，模型为 `OLLAMA_MODEL` 指定的模型

#### Scenario: 向后兼容 OLLAMA_MODEL

- **WHEN** `.env` 中设置了 `OLLAMA_MODEL` 但未设置 `LLM_PROVIDER`
- **THEN** 系统自动推断 `LLM_PROVIDER=ollama`，保持向后兼容

### Requirement: Embedding Provider 配置

系统 SHALL 通过 `EMBEDDING_PROVIDER` 环境变量选择嵌入模型服务商，支持 `zhipu`（默认）、`local`、`siliconflow` 三种 Provider。

#### Scenario: 默认使用智谱 Embedding

- **WHEN** `EMBEDDING_PROVIDER` 未设置或设为 `zhipu`
- **THEN** 系统使用 `ZhipuAIEmbeddings(model="embedding-2")` 生成嵌入向量，API Key 从 `ZHIPU_API_KEY` 环境变量读取

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
