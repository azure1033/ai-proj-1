## ADDED Requirements

### Requirement: 文档上传后自动入库

系统 SHALL 在文档上传成功后自动执行分块、生成嵌入向量、存入向量库的完整入库流程。

#### Scenario: 上传 TXT 文件自动入库

- **WHEN** 用户上传一个 TXT 文件
- **THEN** 系统提取文本内容 → 中文分块 → 生成嵌入向量 → 存入当前会话对应的 ChromaDB collection，并返回分块数量

#### Scenario: 上传 PDF 文件自动入库

- **WHEN** 用户上传一个 PDF 文件
- **THEN** 系统使用 pypdf 提取文本 → 中文分块 → 生成嵌入向量 → 入库，返回分块数量

#### Scenario: 上传 DOCX 文件自动入库

- **WHEN** 用户上传一个 DOCX 文件
- **THEN** 系统使用 python-docx 提取文本 → 中文分块 → 生成嵌入向量 → 入库，返回分块数量

### Requirement: 中文文档智能分块

系统 SHALL 使用 RecursiveCharacterTextSplitter 以中文标点为优先分隔符进行文档分块。

#### Scenario: 按中文标点优先分块

- **WHEN** 文档包含段落、换行、句号、感叹号、问号等中文标点
- **THEN** 系统优先在段落边界处切分，其次在句末标点处切分（`。！？`），再次在分句标点处切分（`；，、`）

#### Scenario: 滑动窗口重叠

- **WHEN** 文档被切分为多个块
- **THEN** 相邻块之间有 chunk_overlap 字符的内容重叠，保证上下文衔接

### Requirement: 嵌入向量生成

系统 SHALL 使用 text2vec-base-chinese 模型将文本块转换为 768 维向量。

#### Scenario: 生成文本块向量

- **WHEN** 文本块内容为中文
- **THEN** 系统调用 text2vec-base-chinese 模型生成归一化的 768 维向量

#### Scenario: 模型未就绪时返回错误

- **WHEN** 嵌入模型加载失败（如网络问题导致无法下载）
- **THEN** 系统向用户返回明确的错误信息，说明模型加载失败，不影响其他 Agent 功能

### Requirement: 分块结果反馈

系统 SHALL 在上传响应中返回文档的分块数量，供前端展示索引状态。

#### Scenario: 上传成功返回分块数

- **WHEN** 文档成功入库
- **THEN** API 响应中包含 `chunks` 字段，值为实际生成的分块数量
