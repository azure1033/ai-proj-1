# PROJECT KNOWLEDGE BASE

**Generated:** 2026-05-15
**Commit:** d659833
**Branch:** master

## OVERVIEW

AI 智能问答助手 — LLM-powered chatbot with Tool-Calling Agent (7 tools), RAG knowledge base, SSE streaming, multi-session management, and MCP server.

- **Backend**: Python + FastAPI + LangChain 1.x + **Zhipu AI `glm-4-flash`** (default) + ChromaDB
- **Frontend**: Vue3 + Vite + TypeScript (no Pinia, no router, no CSS framework)
- **Deploy**: Docker Compose (mysql + backend + frontend + nginx)

## STRUCTURE

```
./
├── backend/              # FastAPI app: main.py (routes+RAG), agent.py, tools/, model_config.py
├── backend/tools/        # 7 LangChain BaseTool subclasses (weather, search, RAG, text, calc)
├── frontend/             # Vue3 SPA: ChatAssistant.vue (monolith), KnowledgePanel, SettingsModal
├── openspec/             # Artifact-driven change management (~70 md files)
├── db/                   # MySQL init.sql (sessions, messages, model_providers)
├── docker-compose.yml    # 3-service orchestration (mysql + backend + frontend)
└── .env                  # LLM_PROVIDER, ZHIPU_API_KEY, database config
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| **Add API route** | `backend/main.py` | All routes in one file (700+ lines); no `routers/` dir |
| **Add Agent tool** | `backend/tools/` → `__init__.py` `get_all_tools()` | Subclass `BaseTool`, define `_run()` |
| **Switch LLM Provider** | `.env` `LLM_PROVIDER=` or DB `model_providers` | Static: `model_config.py`; Dynamic: `provider_manager.py` |
| **Modify RAG pipeline** | `backend/tools/rag_tool.py` | ChromaDB, Chinese splitting, session-isolated collections |
| **Modify chat UI** | `frontend/src/components/ChatAssistant.vue` | 1800+ line monolith: SSE, sessions, i18n, markdown |
| **Modify knowledge panel** | `frontend/src/components/KnowledgePanel.vue` | Drag-drop upload, progress bar, document list |
| **Modify settings** | `frontend/src/components/SettingsModal.vue` | Provider switching, RAG parameter sliders |
| **Change session storage** | `backend/session_store.py` | Dual-mode: MySQL (aiomysql) or in-memory dict |
| **Change management workflow** | `openspec/` | Proposals → designs → specs → tasks → archive |
| **MCP server** | `backend/mcp_server.py` | 7 tools exposed via stdio or streamable-http |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | FastAPI | `backend/main.py:114` | Main app instance, all routes registered here |
| `ask()` | Route | `backend/main.py:372` | Unified chat endpoint, supports `?stream=true` SSE |
| `run_agent()` | Function | `backend/agent.py` | Synchronous agent execution (5 iter max, 30s timeout) |
| `run_agent_stream()` | Generator | `backend/agent.py` | SSE streaming agent execution |
| `get_all_tools()` | Factory | `backend/tools/__init__.py` | Returns 7 LangChain BaseTool instances |
| `get_openai_client()` | Factory | `backend/model_config.py` | OpenAI-compatible client from `.env` |
| `get_provider_manager()` | Singleton | `backend/provider_manager.py` | Runtime provider switching (DB-backed) |
| `api` | Axios | `frontend/src/api.ts` | API client, `baseURL: '/api'` |

## CONVENTIONS

### Backend
- **Tools**: Subclass `BaseTool`, define `_run()`/`_arun()`. Register in `tools/__init__.py` `get_all_tools()`.
- **Tool errors**: Return error strings — do NOT raise exceptions. `return f"失败: {str(e)}"`.
- **Storage**: `USE_MYSQL=true` → async MySQL (aiomysql); unset → in-memory dict. Check `is_mysql_enabled()`.
- **API keys**: Fernet encrypted in DB (`encryption.py`). Key auto-generated on first run into `.env`.
- **RAG**: Collections named `rag_{session_id}_{embedding_id_suffix}`, isolated via `contextvars`.
- **Degradation**: Tavily → DuckDuckGo (search); Zhipu → local(text2vec) → SiliconFlow (embeddings).
- **SSE**: `event: type\ndata: {}\n\n`. Headers: `Cache-Control: no-cache`, `X-Accel-Buffering: no`.
- **CORS**: Explicit allowlist (`localhost:5173`, `5175`, `localhost`, `frontend`), `allow_credentials=True`.

### Frontend
- **No Pinia/Pinia**: All state in component-local `ref()`/`reactive()`, persisted to `localStorage`.
- **No Vue Router**: Single-page; `App.vue` renders only `<ChatAssistant />`.
- **i18n**: Manual `translations` object (zh/en), `t(key)` helper. No vue-i18n package.
- **SSE**: Manual `fetch` + `ReadableStream` parsing (not EventSource API).
- **Styling**: CSS variables + `prefers-color-scheme: dark`. No Tailwind/Bootstrap.
- **TypeScript**: Strict mode, `erasableSyntaxOnly`, `noUnusedLocals`, `noUnusedParameters`.

## ANTI-PATTERNS (THIS PROJECT)

- **DO NOT** call `get_openai_client()` or `get_langchain_llm()` at module level — lazy-init in `_run()`. `tools/text_tools.py:9` and `weather_agent.py:13` violate this.
- **DO NOT** hardcode MySQL credentials in source — `database.py:19` fallback has live credentials.
- **DO NOT** commit `.env` files — `.gitignore` covers `.env` but verify before `git add -f`.
- **DO NOT** import from `session_memory.py` or `session_manager.py` — use `session_store.py`. Old files are compatibility shims.
- **DO NOT** use `provider_manager.get_active_embedding_id()` — method has dead code after `return` on line 56.
- **No test framework exists** — manual testing only. Do not expect `pytest` or `vitest` to work.

## COMMANDS

### Backend (port 8000)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend (port 5173)
```bash
cd frontend
npm install
npm run dev        # Development with HMR
npm run build      # Production: vue-tsc + vite build
```

### Docker
```bash
docker compose up       # mysql + backend + frontend (with HMR)
docker compose build    # Rebuild images
```

### MCP Server
```bash
cd backend
python -m mcp_server                              # stdio (Claude Desktop)
python -m mcp_server --transport streamable-http --port 8765  # HTTP
python test_mcp.py                                # Integration test
```

### Tests (manual only)
```bash
# API smoke test
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"query":"今天北京天气如何"}'
# MCP integration test
cd backend && python test_mcp.py
```

## NOTES

- **Provider default is Zhipu** (not DeepSeek as old docs stated). Switch via `LLM_PROVIDER=` in `.env` or DB `model_providers`.
- **Two `.env` files**: Root (LLM_PROVIDER, ZHIPU_API_KEY) and `backend/` (DEEPSEEK_API_KEY). `model_config.py` reads root via `Path(__file__).parent.parent / ".env"`.
- **Session modules merging**: `session_memory.py` + `session_manager.py` → `session_store.py`. See `openspec/changes/merge-session-modules/`.
- **No CI/CD, no linter, no test framework** — infrastructure needs setup from scratch.
- **MCP HTTP has no auth enforcement** — only warns if `MCP_API_KEY` not set.
- **Dead code**: `provider_manager.py:56-59` `get_active_embedding_id()` has unreachable code after `return`.
- **Sub-AGENTS.md**: See `backend/AGENTS.md`, `backend/tools/AGENTS.md`, `frontend/AGENTS.md`, `openspec/AGENTS.md`.