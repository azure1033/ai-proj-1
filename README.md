# AI 智能问答助手

这是一个基于大语言模型 + Python 全栈开发的轻量级 AI 助手。

## 功能

- AI 问答
- 内容总结
- 文本翻译
- 代码解释
- 天气查询与建议（独立天气 Agent 模块）

## 技术栈

- 后端：Python + FastAPI + LangChain
- AI 核心：DeepSeek 开源大模型
- 前端：Vue3 + Vite
- 天气数据：Open-Meteo API (免费)

## 运行

### 后端

1. 安装依赖：`pip install -r backend/requirements.txt`
2. 设置环境变量：创建 `.env` 文件，添加 `DEEPSEEK_API_KEY=your_key`
3. 运行：`cd backend && uvicorn main:app --reload`

### 前端

1. 安装依赖：`npm install`
2. 运行：`npm run dev`

## API

- POST /ask: 发送查询，返回意图和响应
- POST /weather: 发送城市名称，返回当前天气信息和生活建议

## 目录与模块说明

- `backend/main.py`：核心 FastAPI 应用，负责问答路由和天气路由入口
- `backend/weather_agent.py`：独立天气 agent 模块，负责天气数据获取与建议生成
- `frontend/src/components/Weather.vue`：天气查询前端组件
