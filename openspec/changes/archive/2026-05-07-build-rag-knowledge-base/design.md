## Context

当前项目是一个 AI 智能问答助手（Python FastAPI + LangChain 1.x + Vue3），已实现 SSE 流式响应、Tool-Calling Agent（6 个工具）、文档上传（全量文本内存存储）、多会话管理。文档查询采用"全文塞入 prompt"的原始方式，无法扩展到多文档场景。RAG 知识库是 README 中规划的 P1 优先级功能。

**约束条件**：
- 必须兼容现有 Agent 工具注册模式（`tools/__init__.py` → `get_all_tools()`）
- 必须保持按会话隔离（每个 session 独立的知识库）
- 嵌入模型支持 CPU 推理（开发环境下不一定有 GPU）
- 不破坏现有 6 个工具的功能

## Goals / Non-Goals

**Goals:**
- 实现文档上传 → 分块 → 嵌入 → 向量库存储的完整 RAG 管线
- 将语义检索集成为 Agent 的第 7 个工具（`RAGSearchTool`）
- 按会话隔离知识库数据（每个 session_id 对应独立 ChromaDB collection）
- 前端提供拖拽上传、进度反馈、索引状态可见、参数可配置的用户体验
- RAG 工具始终存在于 Agent 中，无数据时友好告知用户

**Non-Goals:**
- 不实现多模态文档（图片 OCR / 表格解析）——这属于 P2 多模态支持
- 不实现跨会话知识库共享
- 不实现知识库版本管理或增量更新
- 不替换现有文档上传的原始文件存储（uploads/ 目录保留）

## Decisions

### D1: ChromaDB 作为向量库

**选择**: ChromaDB（`langchain-chroma` 包），持久化到 `backend/chroma_db/` 目录。

**替代方案**:
- Milvus Lite: 功能更强大但依赖更重，本地开发需 Docker 或额外进程
- FAISS: 纯内存，不支持原生持久化，需要手动序列化

**理由**: ChromaDB 零配置、内嵌运行、原生持久化、LangChain 一等公民支持。`langchain-chroma` 是官方推荐的当前包（`langchain_community.vectorstores.Chroma` 已废弃）。

### D2: 按会话隔离 Collection

**选择**: 每个 session_id 创建独立 ChromaDB collection，命名规则 `rag_{session_id}`。

**理由**:
- 会话 A 无法检索到会话 B 的文档，保证数据隔离
- 删除会话时可一键清理对应 collection
- 不增加查询复杂度（无需在文档 metadata 中过滤 session_id）

**替代方案**: 全局 collection + metadata 过滤。问题：查询时需额外过滤条件，LLM 调用工具时无法感知 session_id 来做过滤。

### D3: contextvars 传递 session_id

**选择**: 使用 Python `contextvars.ContextVar` 在请求入口设置当前 session_id，RAG 工具内部通过 `get()` 读取。

**理由**:
- Agent 工具 `_run(query)` 签名只接收查询字符串，无法直接传 session_id
- `contextvars` 是 asyncio 原生支持，每个协程独立上下文，并发安全
- 对 Agent 和工具代码零侵入（不需要改工具签名或 LangChain 链）

**替代方案**: 
- LangChain RunnableConfig: 需要修改工具签名为 `_run(query, config)`，对现有工具模板改动大
- Agent 系统提示词注入: 让 LLM 在调用工具时传入 session_id → 不可靠

### D4: 嵌入模型懒加载 + 设置面板可控

**选择**: 默认首次使用时加载模型（`HuggingFaceEmbeddings`）。设置面板提供选项：首次使用时加载 / 启动时预热；推理设备：CPU / GPU。

**理由**:
- 开发阶段 `uvicorn --reload` 频繁重启，启动预热每次等待 15-30 秒严重影响开发效率
- 模型下载/加载失败不影响核心对话功能（天气、翻译等）
- 设置面板让高级用户可选择启动预热以获得更好体验

### D5: RecursiveCharacterTextSplitter + 中文分隔符

**选择**: 自定义分隔符列表（包含中文标点 `。！？；，、`），chunk_size=384, chunk_overlap=64, keep_separator="end"。

**理由**:
- text2vec-base-chinese 最大 512 tokens，384 字符 ≈ 256-512 tokens，在安全范围内
- overlap 64（约 15-20%）保证上下文衔接
- `keep_separator="end"` 避免句号出现在下一块开头（中文阅读体验）

### D6: RAGSearchTool 始终存在

**选择**: 工具始终注册在 `get_all_tools()` 中。知识库为空时 `_run()` 返回友好提示而非报错。

**理由**: 动态添加/移除工具会导致 Agent 行为不一致（用户上传文档前后工具集不同），系统提示词也需动态调整。始终存在的方案更简单可靠。

### D7: 前端组件拆分

**选择**: 从 ChatAssistant.vue 中提取文档面板为独立 `KnowledgePanel.vue`，新增 `SettingsModal.vue` 设置面板。ChatAssistant 通过 props/events 集成。

**理由**: ChatAssistant.vue 已是 1700+ 行单体组件，继续膨胀不利于维护。提取为独立组件后更容易单独开发和测试。

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|---------|
| 嵌入模型首次下载可能超时（模型约 400MB） | 前端显示"模型加载中"状态；设置面板允许切换 CPU/GPU 和加载策略 |
| ChromaDB collection 数量随会话增长 | 删除会话时清理对应 collection；定期检查并清理孤立 collection |
| 中文分块可能在不恰当位置切断（如句子中间） | 自定义中文分隔符优先级；keep_separator="end" 保留句尾标点 |
| contextvars 在非 async 代码路径中可能有边界情况 | 所有 RAG 操作均通过 async handler 或明确设置 context |
| 嵌入向量维度 768，大量文档可能占用较多磁盘 | 暂无缓解（后续可考虑向量压缩或定期清理） |
| `sentence_transformers` 首次安装可能较慢 | requirements.txt 中明确版本号，减少依赖解析时间 |
