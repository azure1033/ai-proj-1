# AI 智能问答助手

> 一个面向实际痛点的全栈 AI Agent 应用 —— 从单体巨石到模块化架构的重构实践。

## 解决了什么问题

| 痛点 | 表现 | 解决方案 | 量化成果 |
|------|------|----------|----------|
| **单体膨胀** | `main.py` 761 行，所有路由、业务逻辑、数据模型挤在一个文件 | 按域拆分为 7 个路由 + 7 个服务 + 7 个 Schema 模块 | `main.py` → **115 行**（缩减 85%） |
| **会话管理断裂** | 前端纯 localStorage，后端完全不知情，新建/删除/重命名不同步 | 启动时 `GET /sessions` 加载，增删改全部走 API | 会话列表与后端**实时一致**，message_count 不再恒为 0 |
| **Provider 配置混乱** | `.env`（静态）和 DB（动态）两套系统并存，module-level init 导致热切换失败 | 统一为 `provider_manager` 单例入口，`model_config` 降级为纯配置读取器 | **2 → 1** 套系统，6 个预设 + 自定义 Provider |
| **重复代码** | `weather_agent.py`（319 行）与 `tools/weather_tool.py`（27 行）各有一套 WeatherTool | 合并为单一 `WeatherTool`，硬编码 150 行城市坐标替换为 LLM 地理编码 | 删除 **356 行**重复/废弃代码 |
| **前端技术债** | Vue 3 单文件组件，无类型安全，无组件复用 | 迁移至 React 18 + TypeScript，9 个函数组件，LocaleContext 国际化 | 组件从 **1 个** 拆为 **9 个** |
| **无错误兜底** | 异常直接暴露为 500 或原始 HTTPException | 3 层全局异常处理器 | 错误响应格式**统一**为 `{"error":"...","detail":"..."}` |

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (React 18 + TS)                   │
│  App.tsx ──┬── AppSidebar (会话 CRUD / 设置 / 知识库)    │
│            └── ChatView (SSE 流式 / Agent 步骤面板)       │
├─────────────────────────────────────────────────────────┤
│                  FastAPI App Factory (115L)               │
│  路由层    routers/ (7 modules)  ← HTTP 协议边界          │
│  服务层    services/ (7 modules) ← 业务逻辑边界            │
│  模型层    schemas/  (7 modules) ← 数据契约边界            │
│  Agent     agent.py              ← LangChain 编排         │
│  工具集    tools/   (7 BaseTool) ← 能力边界               │
├─────────────────────────────────────────────────────────┤
│  存储层    MySQL (会话/消息/Provider) + ChromaDB (向量)    │
│  配置层    .env + DB provider_manager (运行时热切换)       │
│  安全层    Fernet 加密 (API Key) + 异常处理 + CORS         │
└─────────────────────────────────────────────────────────┘
```

**设计原则**：每层有明确的职责边界。路由处理 HTTP 协议，服务处理业务逻辑，Schema 定义数据契约，三者互不越界。

## 技术栈

- **后端**：Python + FastAPI + LangChain 1.x + LangGraph + SQLAlchemy 2.0
- **前端**：React 18 + TypeScript + Vite（零 CSS 框架/状态库依赖）
- **AI**：多 Provider 架构（智谱/DeepSeek/OpenAI/Groq/Ollama/SiliconFlow），运行时热切换
- **存储**：MySQL 8.0（生产）/ 内存 dict（开发）+ ChromaDB 向量持久化
- **部署**：Docker Compose（MySQL + Backend + Frontend + Nginx health check）
- **MCP**：FastMCP 协议暴露 7 个工具（stdio + streamable-http）

## 🚀 快速开始

```bash
# 1. 配置 API Key（项目根目录 .env）
echo "ZHIPU_API_KEY=your_key" > .env

# 2. 一键启动
docker compose up -d --build

# 3. 访问
# 前端: http://localhost:5173
# 后端: http://localhost:8000 (内部)
```

## 📁 项目结构

```
backend/
├── main.py              # App 工厂（115 行）
├── routers/             # 7 个路由模块（HTTP 边界）
├── services/            # 7 个服务模块（业务边界）
├── schemas/             # 7 个 Schema 模块（数据边界）
├── tools/               # 7 个 BaseTool（能力边界）
├── agent.py             # Agent 编排核心
├── provider_manager.py  # 动态 Provider 管理器（单例）
├── model_config.py      # .env 配置读取器
├── session_store.py     # MySQL/内存双模式会话存储
├── encryption.py        # Fernet API Key 加解密
├── models.py            # SQLAlchemy ORM
├── database.py          # MySQL 异步引擎
├── mcp_server.py        # MCP 协议服务器
└── config/logging.py    # 集中日志配置

frontend/src/
├── App.tsx              # 根组件（启动时 GET /sessions 加载）
├── context/LocaleContext.tsx  # zh/en 国际化
└── components/
    ├── AppSidebar.tsx    # 侧边栏 + SettingsModal + KnowledgePanel
    ├── ChatView.tsx      # 聊天区 + SSE 流式（fetch ReadableStream）
    ├── ChatInput.tsx     # 输入框（Enter 发送 / Shift+Enter 换行）
    ├── MessageList.tsx   # 消息列表 + 自动滚动
    ├── MessageBubble.tsx # 消息气泡 + Agent 步骤面板 + Markdown
    └── WelcomeScreen.tsx # 空状态 + 建议问题（可点击发送）
```

## 💡 核心设计决策

### 1. 分层上下文隔离 — 解决"在哪里改什么代码"
路由、服务、Schema 三层各司其职。新增功能只需关注对应层，无需理解全部 761 行代码。每层的修改不会波及到其他层的逻辑。

### 2. Provider 热切换 — 解决"换模型必须重启"
`provider_manager` 单例从 DB 读取活跃 Provider，运行时 `POST /providers/{id}/activate` 即时生效。前端设置面板一键切换，6 个预设 + 自定义 Provider，API Key 加密入库。

### 3. Session 双向同步 — 解决"前端有会话、后端不知道"
启动时 `GET /sessions` 从后端加载 5 个已有会话。创建/删除/重命名全部走 API，localStorage 仅存当前会话 ID。每次消息收发后自动刷新列表，`message_count` 实时准确。

### 4. LLM 地理编码 — 解决"50 个城市不够用"
用 LLM 推断任意城市的经纬度，替换硬编码 150 行 `city_coords`。验证坐标合法性（±90°/±180°），失败时回退 Top-10 城市字典。支持全球任意 LLM 知道的城市的天气查询。

### 5. 安全闭环 — 解决"API Key 明文风险"
**存储**：Fernet 对称加密入库，密钥自动生成写入 `.env`。**传输**：API 响应中 `mask_key()` 脱敏（`sk-...abc1`）。**前端**：输入框 `type="password"`，不可见。

### 6. 评测闭环 — 解决"改了代码不知道有没有坏"
Docker 容器内自动化测试覆盖：Provider CRUD（6 项）、激活/切换、加密脱敏、预设保护、双格式连接测试（OpenAI + Anthropic）。每次改动后 `docker compose up` 即可验证全链路。

## 📡 API

```
POST   /ask?stream=true      SSE 流式对话
POST   /ask                   非流式对话
GET    /sessions              会话列表（含 message_count/preview）
POST   /sessions              创建会话
PATCH  /sessions/{id}          重命名
DELETE /sessions/{id}          删除（级联清理 RAG 向量）
GET    /providers              Provider 列表（Key 脱敏）
POST   /providers              添加自定义 Provider
PUT    /providers/{id}         更新 Key（preset 仅允许改 Key）
POST   /providers/{id}/activate  激活（运行时热切换）
POST   /providers/{id}/test      测试连接（OpenAI + Anthropic 双格式）
POST   /documents/upload        上传文档 → 自动分块 → 向量入库
GET    /rag/status              知识库状态
```

## 🔌 MCP Server

```bash
cd backend
python -m mcp_server                                # stdio
python -m mcp_server --transport streamable-http --port 8765  # HTTP
```

暴露 7 个工具：`get_weather` / `web_search` / `search_knowledge_base` / `summarize_text` / `translate_text` / `explain_code` / `calculator`

---

**版本** 4.1.0 · **最后更新** 2026-06-23
