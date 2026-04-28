# AI 智能问答助手

基于大语言模型 + Python 全栈开发的轻量级 AI 助手，集成了 RAG 知识库、智能意图识别和统一对话界面。

## ✨ 核心功能

### 🎯 智能意图识别
- **天气查询** - 自然语言天气查询，自动提取城市和关注点
- **问答** - 知识型问题回答
- **内容总结** - 长文本总结提取重点
- **文本翻译** - 多语言文本翻译
- **代码解释** - 代码逻辑和功能解释

### 📚 RAG 知识库（已实现）
- 文档上传自动向量化入库（PDF/Word/TXT）
- 中文智能分块（RecursiveCharacterTextSplitter + 中文分隔符）
- 语义检索集成到 Agent 对话流程
- 会话隔离：每个会话独立知识库，互不干扰
- 右侧滑出面板：拖拽上传、进度条、索引状态

### 🤖 Tool-Calling Agent 模式
- 多步推理：自主决定调用哪些工具、按什么顺序
- 7 个工具：天气查询、网页搜索、**知识库检索**、文本总结、翻译、代码解释、计算器
- 智能分流：简单查询走快速路径，复杂查询自动触发 Agent
- 网页搜索：支持 Tavily API / DuckDuckGo，获取实时信息

### 💬 统一对话界面
- 实时聊天对话体验，支持 **SSE 流式响应**（打字效果）
- 自动意图识别和标签显示
- Agent 步骤面板：可展开查看 AI 思考过程
- 多会话管理：左侧边栏创建/切换/重命名/删除会话
- 会话记忆：对话历史持久化，上下文感知回复
- 响应式设计，完美适配各设备

### 🌦️ 天气 Agent 模块
- 50+ 城市支持（中英文）
- 自然语言理解和信息提取
- 针对性生活建议（穿衣、出行、健康等）
- 自动补充信息提示

## 技术栈

- 后端：Python + FastAPI + LangChain 1.x
- AI 核心（多 Provider 架构，.env 切换）：
  - **默认**：智谱 AI `glm-4-flash`（免费云端 LLM）+ `embedding-2`（1024维 Embedding）
  - 回退：Ollama 本地模型 (qwen2.5:3b) + text2vec-base-chinese
  - 备选：SiliconFlow API (DeepSeek)
- 向量数据库：ChromaDB（本地持久化）
- 前端：Vue3 + Vite + TypeScript
- 天气数据：Open-Meteo API (免费)
- 架构模式：Agent + 模块化设计

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Node.js 14+
- 智谱 AI API Key（[免费注册](https://open.bigmodel.cn/)）
- 或 Ollama 本地模型（备选）

### 后端运行

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   在项目根目录创建 `.env` 文件：
   ```bash
   # === 默认：智谱 AI 云端 ===
   LLM_PROVIDER=zhipu
   EMBEDDING_PROVIDER=zhipu
   ZHIPU_API_KEY=your_zhipu_api_key_here

   # === 备选：本地 Ollama ===
   # LLM_PROVIDER=ollama
   # EMBEDDING_PROVIDER=local
   # OLLAMA_MODEL=qwen2.5:3b

   # === 备选：SiliconFlow ===
   # LLM_PROVIDER=siliconflow
   # EMBEDDING_PROVIDER=siliconflow
   # DEEPSEEK_API_KEY=your_api_key_here
   ```

3. **启动服务**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```
   服务运行在：`http://localhost:8000`

### 前端运行

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务**
   ```bash
   npm run dev
   ```
   打开浏览器访问：`http://localhost:5173`

## 📚 API 文档

### 统一对话接口 (推荐)
```
POST /ask
Content-Type: application/json

Body:
{
  "query": "根据我上传的文档，XX是什么",
  "session_id": "optional-session-id"
}

Response (非流式):
{
  "intent": "Agent",
  "response": "基于文档的回答...",
  "session_id": "...",
  "steps": [...]
}

流式响应: POST /ask?stream=true  (SSE)
```

### 知识库接口
```
POST   /documents/upload     # 上传文档 → 自动入库
GET    /documents             # 文档列表（含索引状态）
DELETE /documents/{id}        # 删除单个文档
GET    /rag/status            # 知识库状态
GET    /rag/settings          # 获取 RAG 设置
POST   /rag/settings          # 保存 RAG 设置
```

### 独立天气接口
```
POST /weather
Body: { "query": "北京会下雨吗" }
```

## 📁 项目结构

```
.
├── backend/
│   ├── main.py              # FastAPI应用，Agent路由 + RAG端点
│   ├── agent.py             # Tool-Calling Agent 核心
│   ├── model_config.py      # 多Provider配置 (zhipu/ollama/siliconflow)
│   ├── weather_agent.py     # 天气Agent模块
│   ├── session_memory.py    # 会话记忆与上下文窗口
│   ├── session_manager.py   # 会话元数据管理 (CRUD)
│   ├── tools/               # Agent 工具集
│   │   ├── __init__.py      # 工具注册
│   │   ├── rag_tool.py      # RAG 知识库核心引擎
│   │   ├── weather_tool.py  # 天气查询工具
│   │   ├── web_search.py    # 网页搜索 (Tavily/DDG)
│   │   ├── text_tools.py    # 总结/翻译/代码解释
│   │   └── calculator.py    # 安全计算器
│   ├── chroma_db/           # ChromaDB 向量数据库
│   ├── uploads/             # 上传的原始文件
│   └── requirements.txt     # Python依赖
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主应用组件
│   │   ├── components/
│   │   │   ├── ChatAssistant.vue  # 统一聊天助手 (会话+Agent+SSE)
│   │   │   ├── KnowledgePanel.vue # 知识库管理面板
│   │   │   ├── SettingsModal.vue  # 设置面板 (Provider/参数)
│   │   │   ├── Weather.vue        # 独立天气组件
│   │   │   └── HelloWorld.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── README.md                # 项目说明
├── INTEGRATION_GUIDE.md     # 集成指南
├── TEST_GUIDE.md           # 测试指南
└── .env                    # 环境配置（不提交）
```

## 🔧 核心模块说明

### backend/model_config.py
- 多 Provider 架构：通过 `LLM_PROVIDER` / `EMBEDDING_PROVIDER` 环境变量切换
- 支持 zhipu（智谱 AI）、ollama（本地）、siliconflow 三种 LLM Provider
- 支持 zhipu、local（text2vec）、siliconflow 三种 Embedding Provider
- 向后兼容：自动识别 `OLLAMA_MODEL` 环境变量

### backend/main.py
- `POST /ask` - 统一对话接口，支持 SSE 流式和非流式响应
- `POST /documents/upload` - 文档上传 → 自动分块 → 嵌入 → 入库
- `GET /rag/status` - 知识库状态（文档数、chunk 数、模型状态）
- 会话 API：`/sessions`, `/sessions/{id}`, `/sessions/{id}/history`

### backend/agent.py
- `create_agent(model, tools, prompt)` - LangChain 1.x Tool-Calling Agent
- `run_agent(query)` - 同步执行，返回 `{response, steps}`
- `run_agent_stream(query)` - SSE 流式输出
- 配置：max_iterations=5, max_execution_time=30s

### backend/tools/rag_tool.py — RAG 知识库引擎
- `get_vector_store(session_id)` - ChromaDB 按会话隔离 (collection: `rag_{sid}`)
- `ingest_document(text, metadata, session_id)` - 文档入库
- `search_knowledge(query, session_id, k)` - 语义检索
- `RAGSearchTool` - LangChain BaseTool，集成到 Agent 工具链
- 中文分块：RecursiveCharacterTextSplitter + 中文标点分隔符 + sliding window overlap

### backend/tools/ — Agent 工具集
- `WeatherTool` - 天气查询，50+ 城市支持
- `WebSearchTool` - 网页搜索，Tavily（主）/ DuckDuckGo（备）
- `RAGSearchTool` - 知识库语义检索
- `SummarizeTool` / `TranslateTool` / `ExplainCodeTool` - 文本处理
- `CalculatorTool` - 安全数学计算器

## 💡 使用示例

### 天气查询示例
```
用户输入: "今天合肥热不热，需要穿外套吗？"
系统识别: [天气查询]
系统回复: 
  城市: 合肥
  天气: 晴朗
  温度: 25°C
  湿度: 65%
  建议：温度适中，建议穿一件薄外套...
```

### RAG 知识库示例
```
1. 上传"产品手册.pdf" → 自动分块(12 chunks) → 已索引 ✓
2. 提问: "根据手册，产品保修期是多久？"
3. Agent 调用 search_knowledge_base → 返回相关内容 → 生成回答
```

## 🧪 测试

```bash
# 测试对话
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"今天北京热不热"}'

# 测试 RAG 状态
curl "http://localhost:8000/rag/status?session_id=default"

# 上传文档
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf"
```

详细测试步骤请见 [TEST_GUIDE.md](./TEST_GUIDE.md)

## ❓ 常见问题

### Q: 如何切换 AI 模型？
A: 修改 `.env` 中的 `LLM_PROVIDER` 和 `EMBEDDING_PROVIDER`：
```bash
# 智谱 AI (默认，云端)
LLM_PROVIDER=zhipu
EMBEDDING_PROVIDER=zhipu

# 本地 Ollama
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=local
OLLAMA_MODEL=qwen2.5:3b
```
修改后重启后端服务生效。

### Q: 知识库上传的文档存在哪里？
A: 原始文件在 `backend/uploads/`，向量数据在 `backend/chroma_db/`。删除会话时会自动清理对应向量数据。

### Q: 天气支持哪些城市？
A: 支持50+ 中国主要城市及其英文版本。完整列表见 `backend/weather_agent.py` 中的 `city_coords`。

### Q: 如何添加新的 Agent 工具？
A: 
1. 在 `backend/tools/` 下创建新工具文件（参考 `weather_tool.py` 模板）
2. 在 `backend/tools/__init__.py` 的 `get_all_tools()` 中注册
3. （可选）更新 `backend/agent.py` 的系统提示词

## 📖 文档

- [集成指南](./INTEGRATION_GUIDE.md) - 详细的功能和架构说明
- [测试指南](./TEST_GUIDE.md) - 完整的测试流程和用例

## 🤝 项目构成

- 🤖 **Tool-Calling Agent** - 多步推理，7 工具协作，自主决策
- 📚 **RAG 知识库** - 文档向量化、语义检索、会话隔离
- 🌦️ **天气 Agent** - 自然语言理解的天气查询
- 💬 **统一对话界面** - 实时聊天 + SSE 流式响应 + Agent 步骤可视化
- ⚙️ **多 Provider 架构** - LLM/Embedding 独立可切换，云端本地随时回退
- 🎯 **智能意图识别** - 分层关键词匹配 + LLM 分类 + 复杂度判断
- 📂 **多会话管理** - 侧边栏切换，重命名/删除，历史持久化
- 🧠 **上下文记忆** - 会话记忆 + 上下文窗口 + 用户偏好
- 🔍 **网页搜索** - Tavily API / DuckDuckGo 实时信息获取

## 📝 最后更新

- 版本：3.0.0
- 日期：2026年4月28日
- 主要更新：
  - **RAG 知识库**：文档向量化 + ChromaDB + 语义检索 + 会话隔离
  - **智谱 AI 迁移**：多 Provider 架构，默认 glm-4-flash + embedding-2
  - **SSE 流式响应**：已实现（P0 完成）
  - **前端增强**：KnowledgePanel 右侧滑出面板、SettingsModal 设置面板
  - **布局优化**：flex 自适应 + 知识库抽屉面板

---

## 🔮 未来优化方向

| 优先级 | 方向 | 状态 | 说明 |
|--------|------|------|------|
| ~~P0~~ | ~~流式响应 (SSE)~~ | ✅ 已实现 | 打字效果 + Agent 步骤流式输出 |
| ~~P1~~ | ~~RAG 知识库~~ | ✅ 已实现 | ChromaDB + embedding-2 + 中文分块 |
| P2 | 多模态支持 | 🔜 待规划 | 图片理解、语音输入、Excel 分析 |
| P3 | 对话安全 | 🔜 待规划 | Prompt Injection 防护、内容审查 |
| P4 | 可观测性 | 🔜 待规划 | Token 统计、延迟监控、Dashboard |
| P5 | 用户系统 | 🔜 待规划 | JWT 认证、多租户、用量配额 |
| P6 | MCP 服务器 | 🔜 待规划 | 将项目能力以 MCP 协议暴露 |
