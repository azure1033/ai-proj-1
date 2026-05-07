## 1. 依赖安装与环境准备

- [x] 1.1 在 `backend/requirements.txt` 中添加 RAG 依赖包（`chromadb`, `langchain-chroma>=0.1.2`, `langchain-huggingface`, `sentence_transformers`）
- [x] 1.2 在 `backend/` 目录下执行 `pip install -r requirements.txt` 安装新依赖
- [x] 1.3 验证依赖安装成功：`python -c "import chromadb; from langchain_chroma import Chroma; from langchain_huggingface import HuggingFaceEmbeddings"`

## 2. 后端 RAG 核心引擎（`backend/tools/rag_tool.py` 新建）

- [x] 2.1 实现 `text2vec-base-chinese` 嵌入模型单例管理：`get_embeddings()` 懒加载，HuggingFaceEmbeddings 配置（device="cpu", normalize_embeddings=True）
- [x] 2.2 实现中文文档分块器：RecursiveCharacterTextSplitter，自定义分隔符（\n\n, \n, 。！？；，、），chunk_size=384, chunk_overlap=64, keep_separator="end"
- [x] 2.3 实现 ChromaDB 向量库管理：`get_vector_store(session_id)` 按 `rag_{session_id}` 命名的 collection 隔离，PersistentClient 持久化到 `backend/chroma_db/`
- [x] 2.4 实现 `ingest_document(text, metadata, session_id)` 入库函数：分块 + 嵌入 + 存入向量库，返回 chunk_count
- [x] 2.5 实现 `search_knowledge(query, session_id, k)` 检索函数：语义相似度搜索，格式化结果（含来源文件名和序号）
- [x] 2.6 实现 `RAGSearchTool` 类（继承 BaseTool）：name="search_knowledge_base"，通过 contextvars 获取 session_id，空库返回友好提示
- [x] 2.7 实现 `delete_document_vectors(doc_id, session_id)` 删除向量函数
- [x] 2.8 实现 `delete_session_collection(session_id)` 会话清理函数

## 3. 后端 Agent 集成

- [x] 3.1 在 `backend/tools/__init__.py` 中导入 `RAGSearchTool`，添加到 `get_all_tools()` 返回列表（始终存在）
- [x] 3.2 在 `backend/agent.py` 的 `AGENT_SYSTEM_PROMPT` 中添加 RAG 工具使用指导（何时调用、知识库为空时告知用户上传文档）
- [x] 3.3 确认 `contextvars` session_id 传递：在 `backend/main.py` 的 `/ask` 端点中添加 `set_rag_session(session_id)`

## 4. 后端 API 端点改造

- [x] 4.1 修改 `POST /documents/upload`：上传后调用 `ingest_document()` 自动入库，响应中增加 `chunks` 和 `indexed` 字段；入库失败不影响文件保存
- [x] 4.2 新增 `DELETE /documents/{doc_id}` 端点：删除文档元数据、原始文件和向量数据
- [x] 4.3 修改 `GET /documents`：响应中增加 `chunks` 和 `indexed` 字段
- [x] 4.4 修改 `DELETE /sessions/{session_id}`：删除会话时同步清理对应的 ChromaDB collection
- [x] 4.5 新增 `GET /rag/status` 端点：返回嵌入模型加载状态、当前会话知识库文档数及总 chunk 数
- [x] 4.6 新增 `POST /rag/settings` 端点：接收并持久化 RAG 设置参数
- [x] 4.7 新增 `GET /rag/settings` 端点：返回当前 RAG 设置

## 5. 前端 KnowledgePanel（`frontend/src/components/KnowledgePanel.vue` 新建）

- [x] 5.1 创建组件骨架：模板（拖拽上传区 + 文档列表 + 状态指示）、script setup（props/emits/refs）
- [x] 5.2 实现拖拽上传区：dragover/dragleave/drop 事件，高亮样式，文件类型校验（.txt/.pdf/.docx）
- [x] 5.3 实现文件选择上传：`<input type="file">` 隐藏按钮，点击上传区触发
- [x] 5.4 实现上传进度条：axios `onUploadProgress` 回调，百分比 + 文件大小显示
- [x] 5.5 实现文档列表：显示文件名、分块数、索引状态（"索引中..." / "已索引 ✓" / "索引失败 ✗"），单文档删除按钮
- [x] 5.6 实现知识库状态概览：显示当前会话文档总数、总 chunk 数

## 6. 前端 SettingsModal（`frontend/src/components/SettingsModal.vue` 新建）

- [x] 6.1 创建组件骨架：模态框模板（遮罩 + 内容区 + 关闭）、script setup
- [x] 6.2 实现嵌入模型配置区：当前模型名称显示、推理设备选择（CPU/GPU 单选框）
- [x] 6.3 实现分块参数配置区：chunk_size 滑块（128-1024，默认 384）、chunk_overlap 滑块（0-256，默认 64）
- [x] 6.4 实现检索数量配置区：K 值滑块（1-20，默认 4）
- [x] 6.5 实现模型加载策略配置区：懒加载 / 启动预热 单选框
- [x] 6.6 实现"恢复默认"按钮和"保存设置"按钮，调用 `/rag/settings` API
- [x] 6.7 实现设置在 localStorage 的持久化（`ai-rag-settings` key）

## 7. 前端 ChatAssistant 集成

- [x] 7.1 在 `ChatAssistant.vue` 中引入 `KnowledgePanel` 组件，替换现有内联文档面板模板
- [x] 7.2 在聊天头部/侧边栏添加设置图标（⚙️），点击打开 `SettingsModal`
- [x] 7.3 将现有文档相关状态和方法迁移到 `KnowledgePanel` 组件
- [x] 7.4 实现 ChatAssistant 与 KnowledgePanel 的事件通信
- [x] 7.5 在页面初始化时从 localStorage 加载 RAG 设置并应用到组件

## 8. 验证与测试

- [x] 8.1 运行 `lsp_diagnostics` 检查所有新增/修改的 Python 文件无新 lint 错误
- [x] 8.2 启动后端，验证 `/rag/status` 返回模型就绪状态
- [x] 8.3 上传 TXT 文件，验证自动入库后 `chunks` > 0 且 `indexed: true`
- [x] 8.4 上传 PDF 文件，验证分块 + 嵌入 + 入库完整流程
- [x] 8.5 通过 `/ask` 发送"根据我上传的文档，XX是什么"，验证 Agent 调用 `search_knowledge_base` 工具并返回相关内容
- [x] 8.6 知识库为空时通过 `/ask` 发送"帮我查一下知识库里的东西"，验证 Agent 友好提示
- [x] 8.7 创建两个会话，分别上传不同文档，验证会话间知识库隔离
- [x] 8.8 删除单个文档后验证向量已清理，文档列表更新
- [x] 8.9 删除会话后验证对应 ChromaDB collection 已清理
- [x] 8.10 启动前端，验证拖拽上传、进度条、文档列表状态展示正常
- [x] 8.11 验证设置面板的参数调整和持久化（刷新页面后设置保持）
