## ADDED Requirements

### Requirement: Docker Compose 一键启动
系统 SHALL 提供 `docker-compose.yml`，允许用户通过 `docker compose up -d` 命令一键启动完整的 AI 问答助手应用（前端 + 后端）。

#### Scenario: 首次启动
- **WHEN** 用户在项目根目录执行 `docker compose up -d`
- **THEN** Docker Compose 构建前后端镜像并启动两个容器
- **THEN** 前端通过 `http://localhost` 可访问聊天界面
- **THEN** 后端通过前端 Nginx 的 `/api/*` 代理可访问

#### Scenario: 停止服务
- **WHEN** 用户执行 `docker compose down`
- **THEN** 所有容器停止并移除
- **THEN** 数据卷（ChromaDB、上传文件、会话历史）保留在宿主机

### Requirement: 前端 Nginx 反向代理
前端容器中的 Nginx SHALL 作为反向代理，将 `/api/*` 路径的请求转发到后端 FastAPI 服务，实现前后端同源访问。

#### Scenario: API 请求代理
- **WHEN** 浏览器向 `/api/ask` 发送 POST 请求
- **THEN** Nginx 将请求代理到 `http://backend:8000/ask`
- **THEN** 响应原样返回给浏览器

#### Scenario: SSE 流式代理
- **WHEN** 浏览器向 `/api/ask?stream=true` 发送 POST 请求
- **THEN** Nginx 关闭代理缓冲（`proxy_buffering off`）
- **THEN** SSE 事件实时转发，无延迟

### Requirement: Vue SPA 路由支持
前端 Nginx SHALL 支持 Vue Router 的 history 模式，将所有非文件请求回退到 `index.html`。

#### Scenario: 直接访问子路由
- **WHEN** 浏览器访问 `/some-page`（非文件路径）
- **THEN** Nginx 返回 `index.html`（由 Vue Router 接管路由）
- **THEN** 页面正常渲染对应组件

#### Scenario: 静态资源请求
- **WHEN** 浏览器请求 `/assets/main-abc123.js`（存在的文件路径）
- **THEN** Nginx 直接返回该文件（不触发回退）

### Requirement: 静态资源缓存策略
前端 Nginx SHALL 对不同类型的静态资源应用适当的缓存策略。

#### Scenario: 带 hash 的静态资源
- **WHEN** 浏览器请求 `/assets/` 下的文件（Vite 构建产物含 content hash）
- **THEN** 响应包含 `Cache-Control: public, immutable` 和 1 年过期时间

#### Scenario: index.html 不缓存
- **WHEN** 浏览器请求 `index.html`
- **THEN** 响应包含 `Cache-Control: no-store, no-cache, must-revalidate`
- **THEN** 确保更新部署后用户立即获取最新版本

### Requirement: 数据持久化
后端容器 SHALL 通过 Docker bind mount 将运行时的数据持久化到宿主机，确保容器重启后数据不丢失。

#### Scenario: 容器重启后数据保留
- **WHEN** 容器因更新或故障重启
- **THEN** ChromaDB 向量数据、上传文档、会话历史完整保留
- **THEN** 用户之前的会话和知识库仍然可用

### Requirement: 前后端独立更新
系统 SHALL 支持仅重建并重启单个服务，无需同时更新另一个服务。

#### Scenario: 仅更新后端
- **WHEN** 用户修改后端代码后执行 `docker compose build backend && docker compose up -d backend`
- **THEN** 仅后端容器重建重启
- **THEN** 前端容器不受影响，继续运行

#### Scenario: 仅更新前端
- **WHEN** 用户修改前端代码后执行 `docker compose build frontend && docker compose up -d frontend`
- **THEN** 仅前端容器重建重启
- **THEN** 后端容器不受影响，继续运行

### Requirement: 本地开发不受影响
Docker 部署方案 SHALL 不干扰现有的本地开发工作流。

#### Scenario: 继续使用本地开发
- **WHEN** 用户执行 `cd backend && uvicorn main:app --reload --port 8000` 和 `cd frontend && npm run dev`
- **THEN** 后端在 `localhost:8000` 正常运行，前端在 `localhost:5173` 正常运行
- **THEN** Vite 热更新（HMR）正常工作
