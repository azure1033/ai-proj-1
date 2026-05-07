# 改进路线图：AI 智能问答助手 → 企业级智能客服

> 基于 [IntelliHelp Desk 企业级智能客服与知识管理平台](./IMPROVEMENT_ROADMAP.md) 对标分析制定。
> 目标：在现有 RAG + Agent 基础上做**深度升级**，而非全盘重构。

---

## 当前状态

| 能力 | 状态 |
|------|------|
| Tool-Calling Agent (LangChain 1.x, 7 工具) | ✅ 已具备 |
| RAG 知识库 (ChromaDB + 中文分块 + 会话隔离) | ✅ 已具备 |
| SSE 流式响应 + Agent 步骤可视化 | ✅ 已具备 |
| 多 Provider 架构 (Zhipu/Ollama/SiliconFlow) | ✅ 已具备 |
| 多会话管理 + 上下文记忆 | ✅ 已具备 |
| 前端聊天界面 + 知识库面板 + 设置面板 | ✅ 已具备 |

---

## 改进优先级总览

```
P0 (必做 - RAG 深度)    → P1 (必做 - 工程化)    → P2 (建议)    → P3 (可选)
混检 + 重排                MCP + 重试降级 + PG    监控 + Docker     Redis + MQ + WS
```

---

## P0 — RAG 全链路升级

> 理由：大疆、百度昆仑芯明确要求。当前仅做了向量检索，缺失 BM25 + 重排序两个关键环节。

### 0.1 混合检索（BM25 + 向量 + RRF 融合）

**目标**：将关键词匹配与语义检索结合，通过 RRF (Reciprocal Rank Fusion) 融合排序，提升检索召回率。

**实现要点**：
- 引入 BM25 关键词检索引擎（如 `rank_bm25` 或自建倒排索引）
- 向量检索保持现有 ChromaDB 路径不变
- 实现 RRF 融合算法：`score = Σ 1/(k + rank)`，对两路结果重新排序
- 检索接口统一：`search_knowledge()` 内部并行调用两路，返回融合后的 Top-K

**文件变更**：
- `backend/tools/rag_tool.py`：新增 `BM25Retriever` 类、`hybrid_search()` 函数
- `backend/tools/rag_tool.py`：修改 `search_knowledge()` 支持 `strategy` 参数 (`"hybrid"` / `"vector"` / `"bm25"`)

**验收标准**：
- 对同一查询，混合检索结果应比纯向量检索更精准
- 支持通过 API 参数切换检索策略

---

### 0.2 重排序（Cross-Encoder Reranker）

**目标**：对初步检索结果（Top-K × 2）用 Cross-Encoder 精排，取最终 Top-N 送入 LLM。

**实现要点**：
- 引入轻量级 Cross-Encoder 模型（如 `BAAI/bge-reranker-base` 或 `maidalun1020/bce-reranker-base_v1`）
- 在 `search_knowledge()` 中，混合检索返回后、格式化输出前插入 Rerank 步骤
- 支持可配置：可通过 RAG Settings 开关 Rerank、设置 rerank_top_k
- 懒加载模型，首次使用时才加载到内存

**文件变更**：
- `backend/tools/rag_tool.py`：新增 `Reranker` 类、`rerank()` 函数
- `backend/rag_settings.json`：新增 `rerank_enabled`、`rerank_model`、`rerank_top_k` 字段
- `backend/requirements.txt`：新增 `sentence-transformers` 依赖

**验收标准**：
- Rerank 后的 Top-3 结果与查询相关性明显高于原始排序
- 关闭 Rerank 后回退到原始行为

---

## P1 — 工程化稳定性 + MCP

### 1.1 MCP Server（暴露现有工具能力）

> 理由：苏州全栈岗明确要求；2026 年事实标准，实现成本不高但简历价值极高。

**目标**：将 7 个 Agent 工具以 MCP 协议标准化暴露，让外部 AI 客户端（如 Claude Desktop、Cursor）能发现并调用。

**实现要点**：
- 使用 `mcp` Python SDK 创建 MCP Server
- 每个现有工具封装为一个 MCP Tool（`@server.tool()` 装饰器）
- 天气工具 → `get_weather` MCP Tool
- 网页搜索 → `web_search` MCP Tool
- RAG 检索 → `search_knowledge_base` MCP Tool
- 文本处理工具 → `summarize` / `translate` / `explain_code` MCP Tools
- 计算器 → `calculator` MCP Tool
- 支持 stdio 传输（本地调用）和 SSE 传输（远程调用）两种模式

**文件变更**：
- `backend/mcp_server.py`：MCP Server 入口（新增文件）
- `backend/requirements.txt`：新增 `mcp` 依赖

**验收标准**：
- Claude Desktop 配置后能发现并调用项目工具
- 天气查询、知识库检索等工具可正常被外部调用

---

### 1.2 智能重试 + 指数退避

**目标**：LLM API 调用失败时自动重试，避免单次网络抖动导致整个对话失败。

**实现要点**：
- 在 `agent.py` 的 `run_agent()` / `run_agent_stream()` 外层包装 retry 逻辑
- 退避策略：1s → 2s → 4s → 8s，最多 3 次
- 仅对可重试错误重试（网络超时、429 限流），参数错误直接抛出
- 重试耗尽后返回友好降级消息

**文件变更**：
- `backend/agent.py`：新增 `_with_retry()` 装饰器/包装函数

**验收标准**：
- 模拟网络超时场景，Agent 应自动重试并最终成功
- 3 次重试全部失败后返回降级消息而非 500

---

### 1.3 优雅降级链

**目标**：多层降级确保服务始终可用。

**降级链设计**：
```
用户请求
  → 主 LLM (Zhipu) 不可用
    → 回退 LLM (本地 Ollama) 不可用
      → 返回预设友好消息
  → RAG 检索无结果
    → 自动转通用 LLM 问答（不依赖知识库）
  → Agent 执行超时 (30s)
    → 返回部分结果 + 提示
```

**文件变更**：
- `backend/agent.py`：Agent 执行增加降级分支
- `backend/model_config.py`：新增 `get_fallback_llm()` 函数
- `backend/main.py`：`/ask` 端点增加全局异常兜底

**验收标准**：
- 关闭 Zhipu API Key 后，自动回退到 Ollama 本地模型
- RAG 无结果时自动转为通用问答，不报错

---

### 1.4 PostgreSQL 替代 JSON 文件存储

**目标**：用 PostgreSQL 存储会话、消息历史、用户偏好，替代当前 JSON 文件和内存字典。

**实现要点**：
- 建表：`sessions`、`messages`、`preferences`、`documents`
- 使用 `asyncpg` 或 `psycopg2` 驱动
- 保持现有 API 接口不变，仅替换存储层
- 开发环境用 Docker Compose 一键启动 PostgreSQL
- ChromaDB 继续用于向量存储（不替换）

**文件变更**：
- `backend/database.py`：数据库连接和初始化（新增文件）
- `backend/session_memory.py`：改为读写 PostgreSQL
- `backend/session_manager.py`：改为读写 PostgreSQL
- `backend/main.py`：`DOCUMENTS` 全局列表改为数据库读写
- `docker-compose.yml`：新增 PostgreSQL 服务（根目录）
- `backend/requirements.txt`：新增 `psycopg2-binary`

**验收标准**：
- 重启服务后会话和消息历史不丢失
- 现有多会话 API 行为不变

---

## P2 — 可观测性 + 容器化

### 2.1 Token 用量统计与监控

**目标**：每次 LLM 调用记录 Token 消耗，提供统计端点。

**实现要点**：
- Middleware 拦截每次 LLM 调用，记录 `model`、`prompt_tokens`、`completion_tokens`、`latency_ms`
- 新增 `GET /stats` 端点：返回总调用次数、总 Token 消耗、平均延迟、按模型分组统计
- 可选：新增 `GET /stats/daily` 按天聚合

**文件变更**：
- `backend/monitor.py`：监控中间件（新增文件）
- `backend/main.py`：注册中间件 + `/stats` 端点

**验收标准**：
- 每次对话后 Token 用量自动记录
- `/stats` 端点返回正确统计

---

### 2.2 Docker 容器化

**目标**：一键启动完整服务栈。

**实现要点**：
- `docker-compose.yml`：PostgreSQL + 后端 + 前端 三服务
- 后端 `Dockerfile`：基于 `python:3.11-slim`
- 前端 `Dockerfile`：基于 `node:20-alpine` + nginx
- `.env` 通过环境变量注入

**文件变更**：
- `docker-compose.yml`（根目录）
- `backend/Dockerfile`
- `frontend/Dockerfile`

**验收标准**：
- `docker-compose up` 一键启动，前端可正常访问后端 API

---

### 2.3 意图分流 + 置信度阈值 + 人工接管提示

**目标**：区分不同意图走不同处理链，低置信度时提示转人工。

**实现要点**：
- 意图分类增加「业务查询」「投诉建议」等企业场景类型
- 知识问答 → RAG Agent 链
- 业务查询 → Function Call Agent 链（可对接模拟业务 API）
- 投诉/敏感 → 直接返回转人工提示
- Agent 回答末尾让 LLM 自评置信度 (1-5)，低于 3 分时追加「如需人工协助，请…」

**文件变更**：
- `backend/main.py`：意图分类逻辑增强
- `backend/agent.py`：系统 Prompt 增加置信度自评指令

---

## P3 — 架构扩展（可选）

| 项目 | 说明 | 工作量 |
|------|------|--------|
| Redis 缓存层 | 缓存热门 RAG 查询结果，减少 LLM 调用 | 1 天 |
| 消息队列 (RabbitMQ) | 大文档异步解析入库 | 2 天 |
| WebSocket 实时对话 | 替代 SSE 实现双向实时通信 | 1 天 |
| 文档解析扩展 | 支持 Markdown / HTML / CSV | 0.5 天 |

---

## 实施顺序建议

```
第 1 周：P0.1 混合检索 + P0.2 重排序  →  RAG 全链路完成
第 2 周：P1.2 智能重试 + P1.3 降级链  →  稳定性大幅提升
第 3 周：P1.1 MCP Server              →  简历亮点
第 4 周：P1.4 PostgreSQL              →  数据持久化
第 5 周：P2.1 监控 + P2.2 Docker      →  可观测 + 一键部署
第 6 周：P2.3 意图分流                →  企业场景覆盖
```

---

## 不建议做的事

- ❌ **全盘重写为 Go**：Python + FastAPI 面 AI 应用开发岗完全够用
- ❌ **强行对接虚假 ERP/订单系统**：没有真实系统可对接，做假接口适得其反
- ❌ **拆微服务**：当前阶段单体 FastAPI 架构是正确选择，不必过度设计
- ❌ **引入 Milvus/Weaviate**：ChromaDB 够用，除非数据量上 10 万+ 文档
