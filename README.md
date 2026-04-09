# AI 智能问答助手

这是一个基于大语言模型 + Python 全栈开发的轻量级 AI 助手，集成了智能意图识别和统一对话界面。

## ✨ 核心功能

### 🎯 智能意图识别
- **天气查询** - 自然语言天气查询，自动提取城市和关注点
- **问答** - 知识型问题回答
- **内容总结** - 长文本总结提取重点
- **文本翻译** - 多语言文本翻译
- **代码解释** - 代码逻辑和功能解释

### 💬 统一对话界面
- 实时聊天对话体验
- 自动意图识别和标签显示
- 快速命令按钮
- 完整聊天历史记录
- 响应式设计，完美适配各设备

### 🌦️ 天气 Agent 模块
- 50+ 城市支持（中英文）
- 自然语言理解和信息提取
- 针对性生活建议（穿衣、出行、健康等）
- 自动补充信息提示

## 技术栈

- 后端：Python + FastAPI + LangChain
- AI 核心：DeepSeek 开源大模型
- 前端：Vue3 + Vite + TypeScript
- 天气数据：Open-Meteo API (免费)
- 架构模式：Agent + 模块化设计

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Node.js 14+
- DeepSeek API Key（获取：https://www.siliconflow.cn/）

### 后端运行

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   在項目根目录创建 `.env` 文件：
   ```
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
│   ├── weather_agent.py     # 天气Agent模块，处理天气查询
│   └── requirements.txt     # Python依赖
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主应用组件（使用ChatAssistant）
│   │   ├── components/
│   │   │   ├── ChatAssistant.vue  # 统一聊天助手组件（新）
│   │   │   ├── Weather.vue        # 独立天气组件
│   │   │   └── HelloWorld.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── README.md                # 项目说明
├── INTEGRATION_GUIDE.md     # 集成指南（详细文档）
├── TEST_GUIDE.md           # 测试指南（功能验证）
└── .env                    # 环境配置（不提交）
```

## 🔧 核心模块说明

### backend/main.py
- `classify_intent(query)` - 智能意图分类
  - 天气关键词优先匹配（毫秒级）
  - LLM备选分类（高准确度）
- `ask(request)` - 统一对话接口
  - 自动路由到对应的处理函数
  - 返回意图和响应结果

### backend/weather_agent.py
- `WeatherTool` - 天气数据获取工具
  - 50+ 城市坐标预设
  - Open-Meteo API集成
- `extract_city_from_query()` - 城市提取
- `extract_user_focus()` - 关注点提取
- `get_weather_advice_with_focus()` - 智能建议生成
  - 针对性回答用户问题
  - 补充额外建议

### frontend/components/ChatAssistant.vue
- 实时聊天对话界面
- 意图徽章显示
- 快速命令按钮
- 打字动画反馈
- 自动消息滚动

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

- 📝 **多技能AI Agent** - 问答、总结、翻译、代码解释
- 🌦️ **独立天气Agent** - 自然语言理解的天气查询
- 💬 **统一对话界面** - 实时聊天式交互
- 🎯 **智能意图识别** - 关键词匹配 + LLM分类

## 📝 最后更新

- 版本：2.1.0
- 日期：2026年4月9日
- 主要更新：实现天气Agent与问答助手的统一集成
