## ADDED Requirements

### Requirement: 智谱 Embedding 文档嵌入

系统 SHALL 使用智谱 AI 的 `embedding-2` 模型将文档文本块转换为 1024 维向量。

#### Scenario: PDF 文档入库

- **WHEN** 用户上传 PDF 文件
- **THEN** 系统通过 `ZhipuAIEmbeddings(model="embedding-2")` 调用智谱 API 为每个文本块生成 1024 维向量，存入 ChromaDB，整个流程在 5 秒内完成

#### Scenario: API 调用失败时返回错误

- **WHEN** 智谱 Embedding API 不可用（网络问题或配额耗尽）
- **THEN** 系统在 `ingest_document()` 中捕获异常并返回 `chunks: -1`，告知前端索引失败

### Requirement: 嵌入向量维度兼容

系统 SHALL 确保切换 Embedding Provider 后，不同维度的向量不混用。

#### Scenario: 不同 Provider 使用独立 Collection

- **WHEN** 用户先使用 `EMBEDDING_PROVIDER=zhipu`（1024 维）上传文档，后切换到 `EMBEDDING_PROVIDER=local`（768 维）
- **THEN** 系统为两个 Provider 使用不同的 ChromaDB collection 名称（如 `rag_{sid}` vs `rag_{sid}_local`），避免维度冲突

#### Scenario: 同 Provider 下的向量复用

- **WHEN** 用户保持同一 Provider 上传多份文档
- **THEN** 所有文档向量存入同一个 collection，检索时能跨文档查询

### Requirement: 嵌入 API Key 安全

系统 SHALL 通过环境变量 `ZHIPU_API_KEY` 管理智谱 API 认证，不硬编码或提交到版本控制。

#### Scenario: API Key 从环境变量读取

- **WHEN** 系统初始化 ZhipuAIEmbeddings
- **THEN** API Key 从 `ZHIPU_API_KEY` 环境变量自动读取，无需在代码中显式传递
