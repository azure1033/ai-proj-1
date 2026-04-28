## Why

RAG 知识库的 text2vec-base-chinese 本地嵌入模型首次下载耗时 23+ 分钟（409MB），导致用户上传 PDF 后阻塞在模型下载阶段，前端无任何反馈。切换到智谱 AI 云端 API（LLM + Embedding）可实现秒级响应，同时保留本地 Ollama 和 text2vec 作为回退选项，在隐私/离线场景下仍可使用。

## What Changes

- **新增** 智谱 AI 作为默认 LLM Provider（`glm-4-flash`）和 Embedding Provider（`embedding-2`）
- **新增** `model_config.py` 多 Provider 架构：支持 LLM Provider（zhipu/ollama/siliconflow）和 Embedding Provider（zhipu/local/siliconflow）独立配置
- **修改** `rag_tool.py`：嵌入模型从固定的 `HuggingFaceEmbeddings` 改为可配置的 Provider 模式，默认使用 `ZhipuAIEmbeddings`
- **新增** 依赖 `zhipuai`（`langchain-community` 的智谱集成）
- **修改** `.env`：新增 `ZHIPU_API_KEY`、`LLM_PROVIDER`、`EMBEDDING_PROVIDER` 配置变量
- **修改** 前端设置面板：新增 LLM Provider 和 Embedding Provider 选择

## Capabilities

### New Capabilities

- `multi-provider-config`: 统一的 LLM 和 Embedding Provider 配置系统，通过 `.env` 变量切换，支持 zhipu/ollama/siliconflow（LLM）和 zhipu/local/siliconflow（Embedding）
- `zhipu-llm-integration`: 智谱 AI 大语言模型集成（glm-4-flash 默认），通过 OpenAI 兼容 API 接入 LangChain ChatOpenAI
- `zhipu-embedding-integration`: 智谱 AI 嵌入模型集成（embedding-2 默认），通过 langchain_community 的 ZhipuAIEmbeddings 接入

### Modified Capabilities

- `rag-settings`（来自 build-rag-knowledge-base 变更）：设置面板新增 LLM Provider 和 Embedding Provider 的下拉选择，替代原本只有本地模型配置的界面

## Impact

- **新增依赖**: `zhipuai`（`backend/requirements.txt`）
- **修改文件**: `backend/model_config.py`（重构为多 Provider）、`backend/tools/rag_tool.py`（可配置嵌入 Provider）、`.env`（新增配置变量）、`frontend/src/components/SettingsModal.vue`（新增 Provider 选择）
- **不影响**: Agent 工具管线、文档上传/检索 API、会话管理、SSE 流式响应
- **回退兼容**: 设置 `EMBEDDING_PROVIDER=local` 即可恢复本地 text2vec 模型
