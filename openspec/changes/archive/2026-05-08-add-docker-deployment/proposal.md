## Why

项目目前仅支持本地开发运行（`uvicorn main:app --reload` + `npm run dev`），没有任何生产部署能力。用户希望将 AI 问答助手部署到线上，且能方便地更新代码。Docker 容器化部署是最通用、最可移植的方案 — 构建一次，可以在任何 VPS、PaaS 或自托管平台上运行。

## What Changes

- **新增** `backend/Dockerfile` — FastAPI 后端多阶段 Docker 镜像（Python slim + pip install）
- **新增** `frontend/Dockerfile` — Vue3 前端多阶段构建（node build → nginx serve）
- **新增** `frontend/nginx.conf` — Nginx 配置：SPA 路由回退、静态资源缓存、API 反向代理、SSE 流支持
- **新增** `docker-compose.yml` — 编排 backend + frontend 两个服务，配置数据持久化 volume
- **新增** `.dockerignore` — 排除虚拟环境、node_modules、.git 等无关文件
- **修改** `backend/main.py` — CORS 配置适配 Docker 环境（允许 nginx 代理的内部地址）
- **修改** `frontend/src/components/ChatAssistant.vue` — API 基础地址改为通过环境变量配置（VITE_API_BASE_URL），支持同源代理模式

## Capabilities

### New Capabilities
- `docker-deployment`: 通过 Docker Compose 一键启动完整应用（前端 + 后端），支持数据持久化、SSE 流式响应、前端独立更新

### Modified Capabilities
<!-- 本次变更不修改任何现有功能的规格要求，仅为系统增加部署能力 -->
（无）

## Impact

- **Affected code**: `backend/main.py`（CORS 配置行），`frontend/src/components/ChatAssistant.vue`（axios baseURL）
- **New files**: `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `docker-compose.yml`, `.dockerignore`
- **Dependencies**: 无新增代码依赖。生产环境需要 Docker Engine + Docker Compose
- **Breaking changes**: 无。本地开发方式（`uvicorn` + `npm run dev`）完全不受影响
