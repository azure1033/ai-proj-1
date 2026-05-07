# rag-settings

## Purpose

Settings panel for RAG configuration including chunk parameters, retrieval options, model loading strategy, and provider selection.

## Requirements

### Requirement: 前端设置面板入口

系统 SHALL 在聊天界面提供设置入口，用户可访问 RAG 配置面板。

#### Scenario: 从聊天界面打开设置

- **WHEN** 用户点击聊天界面中的设置图标（⚙️）
- **THEN** 打开设置模态框，默认显示 RAG 知识库配置页面

### Requirement: LLM Provider 设置项

系统 SHALL 在设置面板中提供 LLM Provider 选择，允许用户查看和切换大语言模型服务商。

#### Scenario: 查看当前 LLM Provider

- **WHEN** 用户打开设置面板
- **THEN** 显示当前 LLM Provider（智谱 AI / Ollama 本地 / SiliconFlow），从后端 `/rag/settings` 或环境变量读取

#### Scenario: 切换 LLM Provider

- **WHEN** 用户将 LLM Provider 从"智谱 AI"切换为"Ollama 本地"
- **THEN** 设置保存并提示"需重启服务生效"

### Requirement: Embedding Provider 设置项

系统 SHALL 在设置面板中提供 Embedding Provider 选择。

#### Scenario: 切换 Embedding Provider

- **WHEN** 用户将 Embedding Provider 从"智谱 AI"切换为"本地 text2vec"
- **THEN** 设置保存并提示"需重启服务生效，切换前已索引的文档不受影响"

### Requirement: 嵌入模型配置

系统 SHALL 允许用户在前端设置面板中查看和切换 Embedding Provider（替代原单一的嵌入模型查看）。

#### Scenario: 查看当前 Embedding Provider

- **WHEN** 用户打开设置面板的模型配置区域
- **THEN** 系统显示当前 Embedding Provider 名称（如"智谱 AI - embedding-2"）和推理模式（云端 API / 本地 CPU）

#### Scenario: Provider 切换后模型信息更新

- **WHEN** 用户从"本地 text2vec"切换到"智谱 AI"
- **THEN** 显示智谱 embedding-2 的维度信息（1024 维）替代原本地模型的 CPU/GPU 选项

### Requirement: 分块参数配置

系统 SHALL 允许用户调整文档分块参数（chunk_size 和 chunk_overlap）。

#### Scenario: 调整分块大小

- **WHEN** 用户拖动滑块将 chunk_size 从 384 调整为 256
- **THEN** 设置保存，后续上传的文档按新参数分块

#### Scenario: 调整分块重叠

- **WHEN** 用户拖动滑块将 chunk_overlap 从 64 调整为 128
- **THEN** 设置保存，后续上传的文档按新参数重叠

#### Scenario: 恢复默认参数

- **WHEN** 用户点击"恢复默认"
- **THEN** chunk_size 恢复为 384，chunk_overlap 恢复为 64，检索 K 恢复为 4

### Requirement: 检索数量配置

系统 SHALL 允许用户调整检索返回的文档片段数量。

#### Scenario: 调整检索 K 值

- **WHEN** 用户拖动滑块将检索 K 值从 4 调整为 6
- **THEN** 后续检索返回最多 6 个相关片段

### Requirement: 模型加载策略配置

系统 SHALL 允许用户选择嵌入模型的加载策略。

#### Scenario: 选择懒加载策略

- **WHEN** 用户选择"首次使用时加载"
- **THEN** 嵌入模型在首次需要时才加载，启动速度快但首次上传/查询有延迟

#### Scenario: 选择启动预热策略

- **WHEN** 用户选择"启动时预热"
- **THEN** 嵌入模型在服务启动时加载，启动时间增加但首次使用无延迟

### Requirement: 设置持久化

系统 SHALL 将用户的 RAG 设置持久化保存，服务重启后保持。

#### Scenario: 设置跨会话保持

- **WHEN** 用户调整 RAG 参数并关闭浏览器后重新打开
- **THEN** 之前的设置仍然生效（保存在 localStorage 或后端）
