# AI 智能问答助手

这是一个基于大语言模型 + Python 全栈开发的轻量级 AI 助手，集成了智能意图识别和统一对话界面。

## ✨ 核心功能

### 🎯 智能意图识别
- **天气查询** - 自然语言天气查询，自动提取城市和关注点
- **问答** - 知识型问题回答
- **内容总结** - 长文本总结提取重点
- **文本翻译** - 多语言文本翻译
- **代码解释** - 代码逻辑和功能解释

### 🤖 Tool-Calling Agent 模式
- 多步推理：自主决定调用哪些工具、按什么顺序
- 6 个工具：天气查询、网页搜索、文本总结、翻译、代码解释、计算器
- 智能分流：简单查询走快速路径，复杂查询自动触发 Agent
- 网页搜索：支持 Tavily API / DuckDuckGo，获取实时信息

### 💬 统一对话界面
- 实时聊天对话体验，支持 Markdown 渲染
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

- 后端：Python + FastAPI + LangChain
- AI 核心：Ollama 本地模型 (qwen2.5:3b) 或远程 API
- 前端：Vue3 + Vite + TypeScript
- 天气数据：Open-Meteo API (免费)
- 架构模式：Agent + 模块化设计

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Node.js 14+
- Ollama (本地模型) 或 DeepSeek API Key（远程）

### 后端运行

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   在项目根目录创建 `.env` 文件：
   ```
   # 方式1：使用本地 Ollama
   OLLAMA_MODEL=qwen2.5:3b

   # 方式2：使用远程 API
   DEEPSEEK_API_KEY=your_api_key_here
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
  "query": "今天合肥热不热"
}

Response:
{
  "intent": "天气查询",
  "response": "天气信息和建议..."
}
```

### 独立天气接口
```
POST /weather
Body:
{
  "query": "北京会下雨吗"
}
```

## 📁 项目结构

```
.
├── backend/
│   ├── main.py              # FastAPI应用，统一意图分类和路由
│   ├── agent.py             # Tool-Calling Agent 核心
│   ├── weather_agent.py     # 天气Agent模块
│   ├── session_memory.py    # 会话记忆与上下文窗口
│   ├── session_manager.py   # 会话元数据管理 (CRUD)
│   ├── model_config.py      # 模型配置 (Ollama/API)
│   ├── tools/               # Agent 工具集
│   │   ├── __init__.py      # 工具注册
│   │   ├── weather_tool.py  # 天气查询工具
│   │   ├── web_search.py    # 网页搜索 (Tavily/DDG)
│   │   ├── text_tools.py    # 总结/翻译/代码解释
│   │   └── calculator.py    # 安全计算器
│   └── requirements.txt     # Python依赖
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主应用组件
│   │   ├── components/
│   │   │   ├── ChatAssistant.vue  # 统一聊天助手 (会话+Agent)
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

### backend/main.py
- `classify_complexity(query)` - 复杂度判断，决定走快速路径还是 Agent
- `classify_intent(query)` - 天气关键词分层匹配 + LLM 备选分类
- `ask(request)` - 统一对话接口，自动路由到 Agent 或对应 handler
- 会话 API：`/sessions`, `/sessions/{id}`, `/sessions/{id}/history`
- 文档上传 API：`/documents/upload`, `/documents`

### backend/agent.py
- `create_agent(model, tools, prompt)` - LangChain 1.x Tool-Calling Agent
- `run_agent(query)` - 执行多步推理，返回 `{response, steps}`
- 配置：max_iterations=5, max_execution_time=30s

### backend/tools/ — Agent 工具集
- `WeatherTool` - 封装天气查询，50+ 城市支持
- `WebSearchTool` - 网页搜索，Tavily（主）/ DuckDuckGo（备）
- `SummarizeTool` / `TranslateTool` / `ExplainCodeTool` - 文本处理
- `CalculatorTool` - 安全数学计算器

### backend/session_memory.py
- 会话消息存储（内存 + JSON 文件）
- 上下文窗口：智能截取最近 N 轮对话
- 用户偏好存储：常查城市、语言偏好

### backend/session_manager.py
- 会话元数据 CRUD：创建、查询、更新、删除
- 会话列表：按更新时间排序、预览首条消息

### backend/weather_agent.py
- `WeatherTool` - 天气数据获取工具
- `extract_city_from_query()` - 城市提取
- `extract_user_focus()` - 关注点提取
- `get_weather_advice_with_focus()` - 智能建议生成

### frontend/components/ChatAssistant.vue
- 实时聊天对话界面，Markdown 渲染
- Agent 步骤面板：可折叠展开，显示思考过程
- 会话管理：左侧边栏，创建/切换/重命名/删除
- 响应式设计：移动端可折叠边栏

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
  
  建议：温度适中，建议穿一件薄外套。此外，还要注意防晒，涂上防晒霜。
```

### 问答示例
```
用户输入: "什么是LangChain框架？"
系统识别: [问答]
系统回复: LangChain是一个框架，用于开发由大型语言模型（LLM）驱动的应用程序...
```

### 翻译示例
```
用户输入: "翻译：Good morning"
系统识别: [翻译]
系统回复: 早上好
```

## 🧪 测试

### 快速测试
```bash
# 测试天气查询意图识别
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"今天北京热不热"}'

# 预期响应
{
  "intent": "天气查询",
  "response": "..."
}
```

详细测试步骤请见 [TEST_GUIDE.md](./TEST_GUIDE.md)

## ❓ 常见问题

### Q: 如何更换语言模型？
A: 修改 `backend/main.py` 中的模型参数：
```python
llm = ChatOpenAI(
    model="其他模型名称",
    openai_api_key=os.getenv("API_KEY"),
    openai_api_base="https://api.example.com/"
)
```

### Q: 天气支持哪些城市？
A: 支持50+ 中国主要城市及其英文版本。完整列表见 `backend/weather_agent.py` 中的 `city_coords`。

### Q: 如何添加新的意图类型？
A: 
1. 在 `classify_intent()` 中添加关键词或更新LLM提示词
2. 创建对应的 `handle_xxx()` 函数
3. 在 `/ask` 路由中添加处理分支

### Q: 能否保存聊天历史？
A: 目前只是示例应用，生产环境建议添加数据库存储。可参考 [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) 中的优化方向。

### Q: 前端显示连接失败怎么办？
A: 检查以下几项：
- 后端是否运行在 `http://localhost:8000`
- CORS是否正确配置
- 防火墙是否阻止了连接
- 查看浏览器控制台的错误信息

## 📖 文档

- [集成指南](./INTEGRATION_GUIDE.md) - 详细的功能和架构说明
- [测试指南](./TEST_GUIDE.md) - 完整的测试流程和用例

## 🤝 项目构成

- 🤖 **Tool-Calling Agent** - 多步推理，6 工具协作，自主决策
- 🌦️ **天气 Agent** - 自然语言理解的天气查询
- 💬 **统一对话界面** - 实时聊天式交互，Agent 步骤可视化
- 🎯 **智能意图识别** - 分层关键词匹配 + LLM 分类 + 复杂度判断
- 📂 **多会话管理** - 侧边栏切换，重命名/删除，历史持久化
- 🧠 **上下文记忆** - 会话记忆 + 上下文窗口 + 用户偏好
- 🔍 **网页搜索** - Tavily API / DuckDuckGo 实时信息获取

## 📝 最后更新

- 版本：2.3.0
- 日期：2026年4月27日
- 主要更新：Tool-Calling Agent 模式、多会话管理、网页搜索、Agent 步骤可视化、天气分层关键词优化

---

## 🔮 未来优化方向

以下方向覆盖 AI 应用开发的主要领域，兼顾企业级实践与轻量落地：

### 1. 流式响应 (SSE) ⭐⭐⭐⭐⭐

**是什么**: 字逐字输出，类似 ChatGPT 的打字效果，大幅提升用户体验。

**项目优化方向**:
- 后端实现 Server-Sent Events，`/ask` 支持 `stream=true` 参数
- 前端实现流式消费：打字动画 + Markdown 增量渲染
- Agent 步骤也可流式输出（显示"正在搜索..."、"正在分析..."）

**企业价值**: 生产环境标配，用户感知延迟降低 60%+。

---

### 2. RAG 知识库 ⭐⭐⭐⭐⭐

**是什么**: 将企业私有文档向量化存储，AI 可基于私有知识回答。

**项目优化方向**:
- 集成 Embedding 模型（如 text2vec-base-chinese）
- 接入向量数据库（ChromaDB / Milvus Lite）
- 文档分块策略（sliding window + overlap）
- 前端支持上传 PDF/Word/TXT，自动入库检索

**企业价值**: 企业内部知识库问答、客服机器人、合规文档检索的核心能力。

---

### 3. 多模态支持 ⭐⭐⭐⭐☆

**是什么**: 支持图片、文件等非文本输入，扩展 AI 的感知能力。

**项目优化方向**:
- 图片理解：上传截图让 AI 分析内容（需多模态模型或 OCR）
- 语音输入：浏览器 Web Speech API → 文字 → Agent
- 文件分析：上传 Excel/CSV，AI 进行数据分析和可视化建议

**企业价值**: 财务表格分析、合同扫描件问答、设计稿反馈。

---

### 4. 对话安全与审查 ⭐⭐⭐⭐☆

**是什么**: 防止 Prompt Injection、敏感信息泄露、不适当输出。

**项目优化方向**:
- 输入过滤：检测并拦截恶意 prompt injection 攻击
- 输出审查：敏感词过滤、合规检查
- 审计日志：记录所有对话，支持事后审查
- 速率限制：防止接口滥用

**企业价值**: 合规必备，银行/医疗/政务等行业的强制要求。

---

### 5. 可观测性与监控 ⭐⭐⭐☆☆

**是什么**: 生产环境下的系统运行状态可视化。

**项目优化方向**:
- Token 用量统计：按会话/用户统计消耗
- 延迟监控：P50/P95/P99 响应时间
- 错误追踪：Agent 失败率、工具调用成功率
- 简易 Dashboard：一个 HTML 页面展示核心指标

**企业价值**: 成本控制（token 消耗）、SLA 保障、故障定位。

---

### 6. 用户系统与多租户 ⭐⭐⭐☆☆

**是什么**: 支持多用户、权限管理和数据隔离。

**项目优化方向**:
- 用户注册/登录（JWT 认证）
- 会话归属：每个用户的会话独立不可见
- 用量配额：免费用户 vs 付费用户调用次数限制
- API Key 管理：用户可生成自己的 API Key

**企业价值**: SaaS 化部署的基础，多团队使用场景。

---

### 7. MCP 服务器 ⭐⭐⭐☆☆

**是什么**: 将项目的能力以 MCP 协议暴露，可被 Cursor/Claude/WindSurf 等 AI 工具调用。

**项目优化方向**:
- 实现天气 MCP 服务器：外部 AI 工具可直接查天气
- 实现搜索 MCP 服务器：外部 AI 工具可获得联网能力
- 让项目从"被用户使用"升级为"被 AI 使用"

**企业价值**: 生态整合，让项目成为 AI 工具链的一环。

---

## 📋 推荐开发优先级

| 优先级 | 方向 | 难度 | 收益 | 说明 |
|--------|------|------|------|------|
| P0 | 流式响应 (SSE) | 中 | 极高 | 体验提升最明显，生产环境标配 |
| P1 | RAG 知识库 | 中 | 极高 | 企业级核心能力，问答质量质变 |
| P2 | 多模态支持 | 高 | 高 | 扩展输入形式，覆盖更多场景 |
| P3 | 对话安全 | 低 | 中 | 投入小，合规加分 |
| P4 | 可观测性 | 低 | 中 | 运维基础，方便后期优化 |
| P5 | 用户系统 | 中 | 中 | 多用户/多租户基础 |
| P6 | MCP 服务器 | 中 | 中 | 生态整合，扩展使用边界 |
