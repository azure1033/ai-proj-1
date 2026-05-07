## Why

当前文档上传功能将文档全文直接拼接到 LLM prompt 中（6000字截断），没有语义检索能力，无法扩展到多文档场景。RAG 知识库是 README 规划中的 P1 优先级（企业级核心能力），通过向量化存储和语义检索，使 AI 能基于私有文档精准回答，同时按会话隔离保证多用户场景下的数据安全。

## What Changes

- **新增** ChromaDB 向量存储后端，支持持久化与按会话隔离的 collection
- **新增** 中文文档智能分块（RecursiveCharacterTextSplitter + 中文分隔符 + sliding window overlap）
- **新增** text2vec-base-chinese 嵌入模型集成（懒加载策略，默认首次使用时加载）
- **新增** `RAGSearchTool` 作为第 7 个 Agent 工具，始终存在于工具集中（知识库为空时返回友好提示）
- **新增** 知识库检索 API：`POST /rag/search`、`GET /rag/status`
- **修改** `POST /documents/upload` 端点：上传后自动分块 + 嵌入 + 入库
- **新增** `DELETE /documents/{doc_id}` 端点：删除单个文档及其向量
- **新增** 前端知识库设置面板：嵌入模型选择、分块参数（chunk_size / overlap）、检索 k 值、加载策略
- **增强** 前端文档上传面板：拖拽上传区、上传进度条、文档分块数及索引状态显示
- **修改** Agent 系统提示词：添加 RAG 工具使用指导

## Capabilities

### New Capabilities

- `rag-vector-store`: ChromaDB 向量存储管理，按会话隔离 collection，持久化到本地磁盘
- `rag-document-ingestion`: 文档上传后自动分块、生成嵌入向量、存入向量库的完整入库管线
- `rag-knowledge-retrieval`: 基于语义相似度的知识库检索，作为 Agent 工具集成到对话流程中
- `rag-settings`: 前端可配置的 RAG 参数设置（嵌入模型、分块大小与重叠、检索数量、加载策略）

### Modified Capabilities

- `document-upload`: 原有文档上传增强——上传后自动触发向量入库，新增单文档删除和分块状态展示

## Impact

- **新增依赖**: `chromadb`、`langchain-chroma`、`langchain-huggingface`、`sentence_transformers`（`backend/requirements.txt`）
- **新增文件**: `backend/tools/rag_tool.py`（RAG 工具 + 嵌入模型管理 + 向量库操作）、`frontend/src/components/KnowledgePanel.vue`（知识库管理面板）、`frontend/src/components/SettingsModal.vue`（设置面板）
- **修改文件**: `backend/tools/__init__.py`（注册 RAG 工具）、`backend/agent.py`（系统提示词）、`backend/main.py`（文档上传入库 + 新端点 + session context）、`frontend/src/components/ChatAssistant.vue`（集成新面板和设置入口）
- **不影响**: 现有 6 个 Agent 工具、天气查询、网页搜索、会话管理、SSE 流式响应
