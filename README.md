# AI 智能问答助手

这是一个基于大语言模型 + Python 全栈开发的轻量级 AI 助手。

## 功能

- AI 问答
- 内容总结
- 文本翻译
- 代码解释

## 技术栈

- 后端：Python + FastAPI
- AI 核心：DeepSeek 开源大模型
- 前端：Vue3 + Vite

## 运行

### 后端

1. 安装依赖：`pip install -r requirements.txt`
2. 设置环境变量：创建 `.env` 文件，添加 `DEEPSEEK_API_KEY=your_key`
3. 运行：`uvicorn main:app --reload`

### 前端

1. 安装依赖：`npm install`
2. 运行：`npm run dev`

## API

- POST /ask: 发送查询，返回意图和响应