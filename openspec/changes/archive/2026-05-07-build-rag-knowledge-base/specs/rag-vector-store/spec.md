## ADDED Requirements

### Requirement: ChromaDB 向量库初始化

系统 SHALL 在首次访问时自动初始化 ChromaDB 持久化客户端，数据存储在 `backend/chroma_db/` 目录下。

#### Scenario: 首次启动自动创建存储目录

- **WHEN** 后端服务启动且 `chroma_db/` 目录不存在
- **THEN** 系统自动创建该目录，并以 `PersistentClient` 模式初始化 ChromaDB

#### Scenario: 重启后数据持久化

- **WHEN** 后端服务重启
- **THEN** 之前上传的文档向量数据保持可用，无需重新索引

### Requirement: 按会话隔离的 Collection

系统 SHALL 为每个 session_id 创建独立的 ChromaDB collection，命名规则为 `rag_{session_id}`。

#### Scenario: 创建新会话的知识库

- **WHEN** 用户在会话 A 中上传第一份文档
- **THEN** 系统创建名为 `rag_{session_A_id}` 的 collection，文档向量存入该 collection

#### Scenario: 会话隔离查询

- **WHEN** 用户在会话 A 中查询知识库
- **THEN** 系统仅从 `rag_{session_A_id}` collection 检索，不会返回其他会话的文档

#### Scenario: 删除会话时清理向量库

- **WHEN** 会话被删除
- **THEN** 系统同步删除对应的 `rag_{session_id}` collection 及其所有向量数据

### Requirement: 嵌入模型单例管理

系统 SHALL 以单例模式管理 HuggingFaceEmbeddings 实例，避免重复加载模型权重。

#### Scenario: 多次请求复用模型实例

- **WHEN** 多个请求同时需要生成嵌入向量
- **THEN** 系统使用同一个已加载的模型实例，不重复加载模型权重

#### Scenario: 懒加载策略

- **WHEN** 系统启动且嵌入模型尚未被使用
- **THEN** 模型不加载到内存中，仅在首次需要时触发加载
