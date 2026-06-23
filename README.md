# AI 智能问答助手

基于大语言模型 + Python 全栈开发的轻量级 AI 助手，集成了 RAG 知识库、Tool-Calling Agent 和统一对话界面。

## ✨ 核心功能

### 🤖 Tool-Calling Agent 模式
- 多步推理：自主决定调用哪些工具、按什么顺序
- 7 个工具：天气查询、网页搜索、**知识库检索**、文本总结、翻译、代码解释、计算器
- 智能分流：简单查询走快速路径，复杂查询自动触发 Agent
- 网页搜索：支持 Tavily API / DuckDuckGo，获取实时信息

### 💬 统一对话界面
- 实时聊天对话体验，支持 **SSE 流式响应**（打字效果）
- Agent 步骤面板：可展开查看 AI 思考过程
- 多会话管理：左侧边栏创建/切换/重命名/删除会话
- 会话记忆：对话历史持久化，上下文感知回复
- 中英文国际化（zh/en）
- 暗色/亮色模式自适应
- 响应式设计，适配桌面和移动端

### 📚 RAG 知识库
- 文档上传自动向量化入库（PDF/Word/TXT）
- 中文智能分块（RecursiveCharacterTextSplitter + 中文分隔符）
- 语义检索集成到 Agent 对话流程
- 会话隔离：每个会话独立知识库，互不干扰
- 右侧滑出面板：拖拽上传、进度条、索引状态

### 🌦️ 天气查询
- 自然语言天气查询，LLM 提取城市 + 地理编码
- Open-Meteo API 实时天气数据（免费，无需 API Key）
- 针对性生活建议（穿衣、出行、健康等）

### ⚙️ 多 Provider 架构
- LLM/Embedding 独立可切换，支持运行时热切换无需重启
- 6 个预设 LLM Provider + 4 个预设 Embedding Provider
- API Key Fernet 加密存储，支持自定义 Provider

### 🔌 MCP Server
- 将 7 个工具以 MCP 协议暴露
- 支持 stdio（Claude Desktop）和 streamable-http 两种模式

## 技术栈

- **后端**：Python + FastAPI + LangChain 1.x + LangGraph
- **前端**：React 18 + TypeScript + Vite
- **AI 核心（多 Provider）**：
  - 智谱 AI `glm-4-flash`（默认）+ `embedding-2`
  - DeepSeek / OpenAI / Groq / SiliconFlow / Ollama
- **向量数据库**：ChromaDB（本地持久化）
- **数据库**：MySQL 8.0（生产）/ 内存 dict（开发）
- **天气数据**：Open-Meteo API（免费）
- **部署**：Docker Compose（mysql + backend + frontend + nginx）

## 🚀 快速开始

### 前置要求
- Python 3.10+
- Node.js 18+
- 智谱 AI API Key（[免费注册](https://open.bigmodel.cn/)）

### 本地开发

**1. 配置环境变量**

在项目根目录创建 `.env`：

```bash
LLM_PROVIDER=zhipu
EMBEDDING_PROVIDER=zhipu
ZHIPU_API_KEY=your_zhipu_api_key_here
```

**2. 启动后端**

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

**3. 启动前端**

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

打开浏览器访问：`http://localhost:5173`

### Docker 部署

```bash
docker compose up -d --build
```

服务端口：
- 前端：`http://localhost:5173`
- 后端 API：`http://localhost:8000`（内部）
- MySQL：`localhost:3306`

## 📁 项目结构

```
.
├── backend/
│   ├── main.py                  # FastAPI app 工厂（~115 行）
│   ├── routers/                 # 7 个域路由器
│   │   ├── chat.py              # /ask, /history
│   │   ├── documents.py         # /documents/*
│   │   ├── sessions.py          # /sessions CRUD
│   │   ├── providers.py         # /providers CRUD + activate + test
│   │   ├── rag.py               # /rag/status, /rag/settings
│   │   ├── weather.py           # /weather
│   │   └── preferences.py       # /preferences
│   ├── services/                # 7 个业务逻辑模块
│   │   ├── chat_service.py      # Agent 执行 + SSE 流式
│   │   ├── document_service.py  # 文档上传/删除/列表
│   │   ├── session_service.py   # 会话管理委托
│   │   ├── provider_service.py  # Provider CRUD 业务逻辑
│   │   ├── rag_service.py       # RAG 状态/设置
│   │   └── migration_service.py # 旧数据迁移
│   ├── schemas/                 # 7 个 Pydantic 模型模块
│   ├── config/                  # logging.py 集中日志配置
│   ├── tools/                   # Agent 工具集（7 个 BaseTool）
│   │   ├── rag_tool.py          # RAG 知识库引擎
│   │   ├── weather_tool.py      # 天气查询 + LLM 地理编码
│   │   ├── web_search.py        # Tavily / DuckDuckGo
│   │   ├── text_tools.py        # 总结/翻译/代码解释
│   │   └── calculator.py        # 安全计算器
│   ├── agent.py                 # LangChain Tool-Calling Agent
│   ├── model_config.py          # .env 配置读取器
│   ├── provider_manager.py      # 动态 Provider 管理器（单例）
│   ├── models.py                # SQLAlchemy ORM（sessions + messages + model_providers）
│   ├── database.py              # MySQL 异步引擎 + init_db
│   ├── session_store.py         # 会话存储（MySQL / 内存双模式）
│   ├── encryption.py            # Fernet API Key 加解密
│   ├── mcp_server.py            # MCP 协议服务器
│   ├── requirements.txt         # Python 依赖
│   ├── pyproject.toml           # 项目元数据
│   ├── chroma_db/               # ChromaDB 向量持久化
│   ├── uploads/                 # 上传原始文件
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # 根组件（会话状态管理）
│   │   ├── main.tsx             # React 入口
│   │   ├── api.ts               # Axios 实例
│   │   ├── types.ts             # TypeScript 类型定义
│   │   ├── style.css            # CSS 变量 + 暗色模式 + 响应式
│   │   ├── context/
│   │   │   └── LocaleContext.tsx # 国际化上下文（zh/en）
│   │   └── components/
│   │       ├── AppSidebar.tsx    # 侧边栏 + SettingsModal + KnowledgePanel
│   │       ├── ChatView.tsx      # 聊天区 + SSE 流式处理
│   │       ├── ChatInput.tsx     # 输入框 + 发送按钮
│   │       ├── MessageList.tsx   # 消息列表 + 自动滚动
│   │       ├── MessageBubble.tsx # 消息气泡 + Agent 步骤面板
│   │       └── WelcomeScreen.tsx # 空状态欢迎页
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.app.json
│   ├── nginx.conf
│   └── Dockerfile
├── db/
│   └── init.sql                 # MySQL 建表
├── docker-compose.yml
├── .env                         # 环境变量（不提交）
└── README.md
```

## 📚 API 文档

### 统一对话接口

```
POST /ask?stream=true           # SSE 流式响应
POST /ask                        # 非流式响应

Body: { "query": "...", "session_id": "optional" }
```

### 会话管理

```
GET    /sessions                 # 会话列表
POST   /sessions                 # 创建会话
GET    /sessions/{id}            # 会话详情
PATCH  /sessions/{id}            # 重命名
DELETE /sessions/{id}            # 删除会话
GET    /sessions/{id}/history    # 会话消息历史
```

### 知识库

```
POST   /documents/upload         # 上传文档 → 自动入库
GET    /documents                # 文档列表（含索引状态）
DELETE /documents/{id}           # 删除单个文档
GET    /rag/status               # 知识库状态
GET    /rag/settings             # 获取 RAG 设置
POST   /rag/settings             # 保存 RAG 设置
```

### Provider 管理

```
GET    /providers                # 列出所有 provider（Key 脱敏）
POST   /providers                # 新增自定义 provider
PUT    /providers/{id}           # 更新配置（preset 仅允许改 Key）
DELETE /providers/{id}           # 删除（preset 拒绝）
POST   /providers/{id}/activate  # 激活（即时生效）
POST   /providers/{id}/test      # 测试连接
POST   /providers/test-custom    # 测试自定义连接
```

### 其他

```
POST   /weather                  # 天气查询（自然语言）
POST   /preferences              # 保存用户偏好
GET    /preferences              # 获取偏好
DELETE /preferences              # 删除偏好
GET    /history                  # 获取历史
POST   /history/clear            # 清除历史
```

## 💡 使用示例

```bash
# 对话
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"今天北京热不热"}'

# SSE 流式
curl -X POST "http://localhost:8000/ask?stream=true" \
  -H "Content-Type: application/json" \
  -d '{"query":"你好"}'

# 上传文档
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf"

# 查看 Provider
curl "http://localhost:8000/providers"

# 激活 Provider
curl -X POST "http://localhost:8000/providers/zhipu/activate"
```

## 🔌 MCP Server

将 7 个工具以 MCP 协议暴露，兼容 Claude Desktop、Cursor 等客户端。

```bash
cd backend
python -m mcp_server                              # stdio
python -m mcp_server --transport streamable-http --port 8765  # HTTP
```

### 暴露的工具

| MCP Tool | 功能 |
|----------|------|
| `get_weather` | 天气查询 + 穿衣建议 |
| `web_search` | 互联网搜索 |
| `search_knowledge_base` | 知识库语义检索 |
| `summarize_text` | 文本总结 |
| `translate_text` | 英→中翻译 |
| `explain_code` | 代码解释 |
| `calculator` | 数学计算 |

## ❓ 常见问题

**Q: 如何切换 AI 模型？**

前端设置面板中直接切换，即时生效无需重启。或在 `.env` 中修改 `LLM_PROVIDER`。

**Q: 如何添加新的 Agent 工具？**

1. 在 `backend/tools/` 下创建新工具文件（继承 `BaseTool`）
2. 在 `backend/tools/__init__.py` 的 `get_all_tools()` 中注册
3. 如需独立 API 端点，在 `backend/routers/` 添加路由

**Q: 知识库文档存在哪里？**

原始文件在 `backend/uploads/`，向量数据在 `backend/chroma_db/`。删除会话自动清理。

**Q: 天气支持哪些城市？**

使用 LLM 地理编码，支持 LLM 知道的任何城市（中英文均可），不再依赖硬编码列表。

---

**版本**: 4.0.0 | **日期**: 2026-06-23
