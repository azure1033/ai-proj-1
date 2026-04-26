# AGENTS.md - AI 智能问答助手

## 项目概述

**AI 智能问答助手** - 基于大语言模型的智能对话系统，支持意图识别和统一聊天界面。

- **后端**: Python + FastAPI + LangChain + DeepSeek-V2.5
- **前端**: Vue3 + Vite + TypeScript
- **数据源**: Open-Meteo API (天气)

## 开发命令

### 后端 (端口 8000)
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 前端 (端口 5173)
```bash
cd frontend
npm run dev
```

### 测试 API
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"今天北京天气如何"}'
```

## API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/ask` | POST | 统一对话接口 (推荐) |
| `/weather` | POST | 独立天气查询 |
| `/documents/upload` | POST | 文档上传 (txt/pdf/docx) |
| `/documents` | GET | 列出已上传文档 |
| `/history` | GET | 获取聊天历史 |

**请求格式**:
```json
{"query": "今天合肥热不热，需要穿外套吗？"}
```

**响应格式**:
```json
{"intent": "天气查询", "response": "城市: 合肥\n天气: 晴朗\n..."}
```

## 支持的意图类型

1. **天气查询** - 询问天气、温度、穿衣建议等
2. **问答** - 知识型问题回答
3. **总结** - 长文本内容总结
4. **翻译** - 多语言文本翻译
5. **代码解释** - 代码逻辑解释
6. **文档问答** - 上传文档后自动启用

## 意图分类逻辑

- **天气关键词快速匹配** (<250ms): 包含"天气"、"温度"、"热"、"冷"、"下雨"、"穿"、"风"等关键词
- **LLM 备选分类** (1-2s): 非天气查询使用 DeepSeek-V2.5 分类

## 天气功能

- **支持城市**: 50+ 中国主要城市 (中文/英文)
- **数据源**: Open-Meteo API (免费，无需 API Key)
- **回复内容**: 城市、天气、温度、湿度、风速、空气质量 + 生活建议

## 环境配置

`.env` 文件 (项目根目录):
```
DEEPSEEK_API_KEY=sk-xxx  # 从 https://www.siliconflow.cn/ 获取
```

## CORS 配置

后端允许的源:
- `http://localhost:5173` (前端开发服务器)
- `http://localhost:5175` (备用端口)

## 核心文件

| 文件 | 说明 |
|------|------|
| `backend/main.py` | FastAPI 应用、意图分类、路由 |
| `backend/weather_agent.py` | 天气工具、城市坐标、建议生成 |
| `frontend/src/components/ChatAssistant.vue` | 统一聊天界面组件 |
| `frontend/src/App.vue` | 主应用组件 |

## 测试用例

```bash
# 天气查询
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"query":"今天合肥热不热"}'

# 问答
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"query":"什么是LangChain"}'

# 翻译
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"query":"请翻译：Hello world"}'

# 总结
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"query":"请总结：人工智能是..."}'
```

## 故障排查

- **前端显示"连接失败"**: 检查后端是否运行在 localhost:8000
- **意图识别错误**: 确保输入包含明确的关键词，或等待 LLM 分类 (1-2s)
- **天气查询失败**: 检查网络连接，确认城市在支持列表中

## 依赖安装

```bash
# 后端
cd backend && pip install -r requirements.txt

# 前端
cd frontend && npm install
```

## 已安装的 npm 包

- `vue`: ^3.5.30
- `axios`: ^1.14.0
- `vite`: ^8.0.1
- `typescript`: ~5.9.3
- `vue-tsc`: ^3.2.5

## 文档

- `README.md` - 项目说明
- `INTEGRATION_GUIDE.md` - 集成指南
- `TEST_GUIDE.md` - 测试指南
- `COMPLETION_SUMMARY.md` - 完成总结