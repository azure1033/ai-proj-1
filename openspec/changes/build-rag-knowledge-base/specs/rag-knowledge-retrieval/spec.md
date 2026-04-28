## ADDED Requirements

### Requirement: RAG 检索 Agent 工具

系统 SHALL 提供一个名为 `search_knowledge_base` 的 LangChain 工具，供 Agent 在需要检索私有文档时调用。

#### Scenario: Agent 调用 RAG 工具检索文档

- **WHEN** 用户问"根据我上传的文档，XX 是什么意思"
- **THEN** Agent 调用 `search_knowledge_base` 工具，传入用户查询，工具返回语义相似度最高的文档片段

#### Scenario: 知识库为空时的友好提示

- **WHEN** Agent 调用 RAG 工具，但当前会话的知识库为空
- **THEN** 工具返回"当前知识库中暂无文档。请先上传文档后再查询。"，Agent 据此告知用户

### Requirement: 语义相似度检索

系统 SHALL 使用余弦相似度检索与查询最相关的文档片段。

#### Scenario: 返回 Top-K 相关片段

- **WHEN** 用户查询"产品价格是多少"
- **THEN** 系统返回语义相似度最高的 K 个（默认 4 个）文档片段，按相似度降序排列

#### Scenario: 无相关结果

- **WHEN** 查询内容与知识库中的所有文档均不相关（相似度极低）
- **THEN** 系统返回"知识库中未找到相关内容"并建议用户换个方式提问

### Requirement: 检索结果格式化

系统 SHALL 将检索到的文档片段格式化为包含来源信息的结构化文本，供 Agent 理解和使用。

#### Scenario: 单文档检索结果

- **WHEN** 检索命中一个文档的多个片段
- **THEN** 返回结果包含 `[1] 来源: 文件名` 前缀和片段内容，以分隔线隔开

#### Scenario: 多文档检索结果

- **WHEN** 检索命中多个不同文档的片段
- **THEN** 返回结果按文档分组，每个片段标注来源文件名

### Requirement: 检索参数可配置

系统 SHALL 允许通过设置面板调整检索参数。

#### Scenario: 调整检索数量 K

- **WHEN** 用户在设置中将检索数量从 4 改为 8
- **THEN** 后续检索返回最多 8 个相关片段
