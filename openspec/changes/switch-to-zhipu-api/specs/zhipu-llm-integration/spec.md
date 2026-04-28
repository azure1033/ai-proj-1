## ADDED Requirements

### Requirement: 智谱 LLM 对话集成

系统 SHALL 将智谱 AI 的 `glm-4-flash` 模型集成为默认对话 LLM。

#### Scenario: 正常对话

- **WHEN** 用户通过 `/ask` 发送"北京天气怎么样"
- **THEN** Agent 使用 `ChatOpenAI(model="glm-4-flash", base_url="https://open.bigmodel.cn/api/paas/v4/")` 进行推理，正常返回天气查询结果

#### Scenario: API Key 鉴权失败

- **WHEN** `ZHIPU_API_KEY` 无效或未设置
- **THEN** 系统返回明确的错误信息，提示检查 API Key 配置

### Requirement: 智谱 LLM 与现有 Agent 工具兼容

系统 SHALL 确保智谱 LLM 与现有的 7 个 Agent 工具（含 RAGSearchTool）完全兼容。

#### Scenario: 智谱 LLM 调用天气工具

- **WHEN** 用户问天气相关问题
- **THEN** 智谱 LLM 能正确识别并调用 `get_weather` 工具，效果与 Ollama/SiliconFlow 一致

#### Scenario: 智谱 LLM 调用知识库检索工具

- **WHEN** 用户询问已上传文档内容
- **THEN** 智谱 LLM 能正确识别并调用 `search_knowledge_base` 工具
