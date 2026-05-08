## Context

项目当前仅支持本地开发：后端通过 `uvicorn main:app --reload --port 8000` 启动，前端通过 `npm run dev`（Vite dev server，端口 5173）。两者独立运行，前端通过 `localhost:8000` 直连后端。没有容器化、没有反向代理、没有生产构建流程。

目标：为项目增加 Docker 容器化部署能力，支持一键启动完整应用，且更新代码时只需重建变更的服务。

约束：
- 不能破坏现有本地开发流程
- 嵌入模型使用 zhipu API（镜像无需 PyTorch）
- 密钥管理先用 env_file，后续再升级
- 前端通过 nginx 同源代理访问后端（无需 CORS 跨域配置）

## Goals / Non-Goals

**Goals:**
- 通过 `docker compose up -d` 一键启动完整应用
- 前端 Nginx 提供 SPA 路由支持、静态资源缓存、API 反向代理
- 后端数据（ChromaDB、上传文件、会话历史）持久化到宿主机
- SSE 流式响应正常工作
- 支持仅重建单个服务（`docker compose build backend` / `frontend`）实现独立更新
- 前后端同源（nginx 代理 `/api/*`），浏览器只需一个 origin

**Non-Goals:**
- 不涉及 CI/CD 流水线配置（后续单独考虑）
- 不引入数据库或 Redis（沿用现有文件存储）
- 不实现 HTTPS/SSL（本地 Docker 环境使用 HTTP，生产 SSL 由外部网关处理）
- 不实现健康检查探活（后续单独添加 `/health` 端点）
- 不实现零停机部署（当前规模不需要）
- 不修改任何现有功能的行为逻辑

## Decisions

### 决策 1：两容器架构（非三容器）

**选择**：`frontend-nginx` + `backend`，共 2 个容器。Nginx 内置在前端镜像中。

**替代方案**：单独 Nginx 容器 + 前端容器 + 后端容器（3 容器）。
**理由**：对于本项目规模，将 Nginx 与前端的 Vue 静态文件放在同一容器中减少了网络跳转和配置复杂度。前端镜像通过多阶段构建（`node build` → `nginx serve`）实现，最终镜像 < 50MB。

### 决策 2：同源代理，消除 CORS

**选择**：Nginx 将 `/api/*` 请求代理到 `backend:8000`，前端使用相对路径 `/api/ask` 调用。浏览器视角只有一个 origin。

**替代方案**：前端直连后端（需要 CORS 配置生产域名）。
**理由**：同源代理更简洁，不需要维护 CORS origins 白名单。后续无论部署到哪个平台（VPS、Railway、Coolify），都无需调整 CORS。

**影响**：
- `ChatAssistant.vue` 的 axios baseURL 改为通过 `VITE_API_BASE_URL` 环境变量配置，开发时设为 `http://localhost:8000`，生产构建时不设（走同源代理）
- `main.py` 的 CORS 保留 `localhost:5173`（开发用），额外添加 Docker 内部地址作为兜底

### 决策 3：多阶段 Docker 构建

**选择**：前后端均采用多阶段构建。

**后端 Dockerfile**：
- Stage 1（`builder`）：`python:3.12-slim`，安装 gcc 等编译依赖，`pip install` 到独立路径
- Stage 2（`runtime`）：`python:3.12-slim`，只复制 pip 包和源码，非 root 用户运行
- 依赖层缓存：先 `COPY requirements.txt` 再 `RUN pip install`，利用 Docker layer cache
- 最终镜像 ~200MB（zhipu 嵌入模式，无 PyTorch）

**前端 Dockerfile**：
- Stage 1（`builder`）：`node:22-alpine`，`npm ci && npm run build`
- Stage 2（`runtime`）：`nginx:1.27-alpine`，复制 `dist/` + nginx 配置
- 最终镜像 < 50MB

### 决策 4：SSE 流式代理配置

**选择**：在 nginx 的 `/api/` location 块中设置 `proxy_buffering off;` 和 `proxy_cache off;`。

**理由**：FastAPI 的 `/ask?stream=true` 使用 SSE（Server-Sent Events），Nginx 默认会缓冲代理响应，导致流式输出被阻塞直到响应完成。关闭缓冲后，每个 SSE 事件立即转发给客户端。

### 决策 5：数据持久化策略

**选择**：通过 Docker bind mount 将三个数据目录挂载到宿主机：

| 容器路径 | 宿主机路径 | 内容 |
|----------|-----------|------|
| `/app/chroma_db/` | `./backend/chroma_db/` | RAG 向量数据库 |
| `/app/uploads/` | `./backend/uploads/` | 用户上传文档 |
| `/app/chat_history.json` | `./backend/chat_history.json` | 会话历史 |

**替代方案**：Docker named volumes。
**理由**：bind mount 更直观，数据直接可见于项目目录。对于单机部署场景足够。

## Risks / Trade-offs

- **[风险] Nginx 在前端容器中，更新前端会短暂中断** → 当前后端继续响应（nginx 重启需 ~1 秒）。对个人项目可接受。
- **[风险] ChromaDB 使用本地文件，无法多实例共享** → 当前单实例部署，无需考虑。未来扩展时再迁移到独立向量数据库。
- **[风险] .env 文件通过 env_file 注入，密钥以明文存在于宿主机** → 先用 env_file，后续升级为 Docker secrets。
- **[风险] 无健康检查，Docker Compose 无法检测服务就绪** → 当前影响有限（小项目启动快），后续可为后端添加 `/health` 端点。
