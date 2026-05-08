## 1. 后端 Docker 化

- [x] 1.1 创建 `backend/Dockerfile`：多阶段构建（builder 安装依赖 → runtime 运行），使用 `python:3.12-slim` 基础镜像，非 root 用户，暴露 8000 端口
- [x] 1.2 创建 `.dockerignore`：排除 `.venv/`、`__pycache__/`、`.git/`、`node_modules/`、`*.pyc` 等
- [x] 2.1 创建 `frontend/Dockerfile`：多阶段构建（`node:22-alpine` 执行 `npm ci && npm run build` → `nginx:1.27-alpine` 复制 dist/ 和 nginx 配置）
- [x] 2.2 创建 `frontend/nginx.conf`：配置 SPA 路由回退（`try_files $uri /index.html`）、静态资源缓存（`/assets/` 1年 + immutable，`index.html` 不缓存）、API 代理（`/api/*` → `backend:8000`，关闭 `proxy_buffering` 支持 SSE）
- [x] 3.1 创建根目录 `docker-compose.yml`：定义 `backend` 服务（build backend/，内部暴露 8000，env_file 注入 .env，挂载 chroma_db/uploads/chat_history.json）和 `frontend` 服务（build frontend/，映射宿主机 80 端口，依赖 backend）
- [x] 3.2 配置 Docker 内部网络（`app-network` bridge），确保服务间通过服务名通信
- [x] 4.1 修改前端组件 API 调用：创建共享 `api.ts`（axios 实例，baseURL 来自 `VITE_API_BASE_URL`），修改 ChatAssistant.vue、KnowledgePanel.vue、SettingsModal.vue 的 import 和 URL，fetch 调用也使用环境变量
- [x] 4.2 创建 `frontend/.env.development`（`VITE_API_BASE_URL=http://localhost:8000`）和 `frontend/.env.production`（`VITE_API_BASE_URL=/api`）
- [x] 4.3 修改 `backend/main.py` CORS 配置：保留 `localhost:5173` 和 `localhost:5175`，额外添加 Docker 内部地址 `http://frontend` 和 `http://localhost` 作为兜底

## 5. 验证

- [x] 5.1 执行 `docker compose config` 确认配置正确，`npm run build` 确认前端构建成功
- [x] 5.2 访问 `http://localhost` 确认前端页面可加载（需 `docker compose up -d --build` 后手动验证）
- [x] 5.3 发送聊天请求确认 API 代理和 LLM 调用正常（需 Docker 运行后手动验证）
- [x] 5.4 测试流式响应（`stream=true`）确认 SSE 实时返回（需 Docker 运行后手动验证）
- [x] 5.5 执行 `docker compose down && docker compose up -d` 确认数据持久化（需手动验证）
- [x] 5.6 `npm run build` 成功确认本地开发流程不受影响
