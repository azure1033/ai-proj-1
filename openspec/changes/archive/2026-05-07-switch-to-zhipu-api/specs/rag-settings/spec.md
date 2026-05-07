## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: 嵌入模型配置

系统 SHALL 允许用户在前端设置面板中查看和切换 Embedding Provider（替代原单一的嵌入模型查看）。

#### Scenario: 查看当前 Embedding Provider

- **WHEN** 用户打开设置面板的模型配置区域
- **THEN** 系统显示当前 Embedding Provider 名称（如"智谱 AI - embedding-2"）和推理模式（云端 API / 本地 CPU）

#### Scenario: Provider 切换后模型信息更新

- **WHEN** 用户从"本地 text2vec"切换到"智谱 AI"
- **THEN** 显示智谱 embedding-2 的维度信息（1024 维）替代原本地模型的 CPU/GPU 选项
