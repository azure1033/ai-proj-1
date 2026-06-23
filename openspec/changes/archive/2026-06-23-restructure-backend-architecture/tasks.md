## 1. Directory Structure Setup

- [x] 1.1 Create `backend/schemas/` directory with `__init__.py`
- [x] 1.2 Create `backend/routers/` directory with `__init__.py`
- [x] 1.3 Create `backend/services/` directory with `__init__.py`
- [x] 1.4 Create `backend/config/` directory with `__init__.py`
- [x] 1.5 Verify all new directories exist and are importable: `python -c "import schemas; import routers; import services; import config"`

## 2. Extract Pydantic Schemas

- [x] 2.1 Create `schemas/chat.py` — move `QueryRequest` from `main.py`
- [x] 2.2 Create `schemas/documents.py` — document-related response models (no request models needed, `UploadFile` is FastAPI built-in)
- [x] 2.3 Create `schemas/sessions.py` — move `CreateSessionRequest`, `UpdateSessionRequest` from `main.py`; add `SessionResponse`
- [x] 2.4 Create `schemas/providers.py` — move `ProviderCreateRequest`, `ProviderUpdateRequest`, `ProviderTestRequest`, `ProviderTestCustomRequest` from `main.py`
- [x] 2.5 Create `schemas/rag.py` — move `RagSettingsRequest` from `main.py`
- [x] 2.6 Create `schemas/weather.py` — move `WeatherRequest` from `main.py`
- [x] 2.7 Create `schemas/preferences.py` — move `PreferencesRequest` from `main.py`
- [x] 2.8 Update `main.py` imports to use new schema modules; verify no Pydantic models remain inline
- [x] 2.9 Run `python -c "from schemas.chat import QueryRequest; print(QueryRequest(query='test'))"` to verify all schemas import correctly

## 3. Create Service Layer

- [x] 3.1 Create `services/chat_service.py` — extract `handle_chat_query()` from `main.py` `/ask` endpoint logic (Agent execution, SSE streaming, message persistence)
- [x] 3.2 Create `services/document_service.py` — extract `upload_document()`, `list_documents()`, `delete_document()`, `clear_documents()` from `main.py`; move `extract_text_from_file()`, `save_uploaded_file()`, `append_document()`, `get_documents_context()`, `handle_document_query()` from `main.py`
- [x] 3.3 Create `services/session_service.py` — thin delegation layer wrapping `session_store.py` functions (list, create, get, update, delete sessions)
- [x] 3.4 Create `services/provider_service.py` — extract provider CRUD, activation, and test logic from `main.py` provider endpoints
- [x] 3.5 Create `services/rag_service.py` — extract RAG status query and settings save/load from `main.py`
- [x] 3.6 Move `_migrate_chat_history_json()` from `main.py` to `services/chat_service.py` (or `services/migration.py`)
- [x] 3.7 Verify all service functions are independently importable: `python -c "from services.chat_service import handle_chat_query; from services.document_service import upload_document"`

## 4. Create Domain Routers

- [x] 4.1 Create `routers/chat.py` — `/ask` (POST, supports `?stream=true`), `/history` (GET), `/history/clear` (POST)
- [x] 4.2 Create `routers/documents.py` — `/documents/upload` (POST), `/documents` (GET), `/documents` (DELETE), `/documents/{doc_id}` (DELETE)
- [x] 4.3 Create `routers/sessions.py` — `/sessions` (GET, POST), `/sessions/{id}` (GET, PATCH, DELETE), `/sessions/{id}/history` (GET)
- [x] 4.4 Create `routers/providers.py` — `/providers` (GET, POST), `/providers/{id}` (PUT, DELETE), `/providers/{id}/activate` (POST), `/providers/{id}/test` (POST), `/providers/test-custom` (POST)
- [x] 4.5 Create `routers/rag.py` — `/rag/status` (GET), `/rag/settings` (GET, POST)
- [x] 4.6 Create `routers/weather.py` — `/weather` (POST)
- [x] 4.7 Create `routers/preferences.py` — `/preferences` (GET, POST, DELETE)
- [x] 4.8 Verify each router file is syntactically valid: `python -m py_compile routers/*.py`

## 5. Slim Down main.py

- [x] 5.1 Remove all route handler functions from `main.py` (keep only `app = FastAPI()`, CORS middleware, startup event, root `/` endpoint)
- [x] 5.2 Add `app.include_router()` calls for all 7 routers from `routers/`
- [x] 5.3 Update startup event to import migration function from new location
- [x] 5.4 Remove `UPLOAD_DIR`, `DOCUMENTS`, `HISTORY_FILE` module-level globals (moved to services)
- [x] 5.5 Remove `extract_text_from_file()`, `save_uploaded_file()`, `append_document()`, `get_documents_context()`, `handle_document_query()`, `handle_qa()`, `handle_qa_with_context()`, `handle_summarize()`, `handle_translate()`, `handle_code_explain()` (moved to services; unused legacy handlers deleted)
- [x] 5.6 Verify `main.py` is ~100 lines: `wc -l backend/main.py`
- [x] 5.7 Start server: `cd backend && python -m uvicorn main:app --port 8000` — verify all endpoints respond correctly

## 6. Consolidate Weather Tool

- [x] 6.1 Rewrite `tools/weather_tool.py` `WeatherTool._run()` to accept natural language queries (not just city name)
- [x] 6.2 Add LLM-based city extraction: use active LLM to extract city name from query
- [x] 6.3 Add LLM-based geocoding: use active LLM to resolve city → `{lat, lon}` coordinates
- [x] 6.4 Add coordinate validation: ensure lat in [-90, 90], lon in [-180, 180]
- [x] 6.5 Add weather advice generation: use active LLM to produce advice from raw weather data
- [x] 6.6 Keep a small fallback dict of top-10 cities for when LLM geocoding fails
- [x] 6.7 Update `tools/__init__.py` if import path changes
- [x] 6.8 Delete `backend/weather_agent.py`
- [x] 6.9 Verify: `python -c "from tools.weather_tool import WeatherTool; t = WeatherTool(); print(t._run('北京今天热不热'))"` returns valid weather advice

## 7. Unify Provider Initialization

- [x] 7.1 Refactor `model_config.py` to export `read_llm_config() -> dict` and `read_embedding_config() -> dict` instead of client factory functions
- [x] 7.2 Remove `get_openai_client()` and `get_langchain_llm()` from `model_config.py`
- [x] 7.3 Update `provider_manager.py` `_reload_llm_sync()` and `_reload_embedding_sync()` to call `model_config.read_*_config()` and construct clients from the returned dicts
- [x] 7.4 Remove dead code: `get_active_embedding_id()` unreachable lines after `return` on line 56
- [x] 7.5 Fix `tools/text_tools.py` — remove module-level `client` init; ensure `_get_client_and_model()` always does lazy-init via `provider_manager`
- [x] 7.6 Audit all imports of `model_config`: ensure no code calls removed functions (`get_openai_client`, `get_langchain_llm`). Update to use `provider_manager` or `read_*_config()`.
- [x] 7.7 Verify provider hot-switching still works: start server, switch provider via API, send chat message — confirm it uses new provider

## 8. Cleanup & Anti-Pattern Fixes

- [x] 8.1 Delete `backend/session_memory.py`
- [x] 8.2 Delete `backend/session_manager.py`
- [x] 8.3 Update `main.py` imports: `from session_store import ...` instead of `from session_memory import ...` or `from session_manager import ...`
- [x] 8.4 Audit entire codebase for remaining references to `session_memory` or `session_manager`: `grep -r "session_memory\|session_manager" backend/` — fix any remaining
- [x] 8.5 Replace module-level `DOCUMENTS: list[dict]` in document service with session-scoped dict `_document_registry: dict[str, list[dict]]`
- [x] 8.6 Remove hardcoded fallback credentials from `database.py:19` — ensure all DB credentials come from `.env` / environment variables
- [x] 8.7 Verify `mcp_server.py` imports `get_all_tools` from `tools` correctly (it already does, but verify after restructuring)

## 9. Add Error Handling & Logging

- [x] 9.1 Create `config/logging.py` — centralized logging configuration with format, level from env var `LOG_LEVEL` (default INFO)
- [x] 9.2 Add global `HTTPException` handler in `main.py` returning `{"error": "...", "detail": "..."}` format
- [x] 9.3 Add global `RequestValidationError` handler returning field-level validation errors
- [x] 9.4 Add global unhandled `Exception` handler logging full traceback and returning generic 500
- [x] 9.5 Update `main.py` to call logging config at startup
- [x] 9.6 Verify error format: `curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"query": 123}'` returns `{"error": "Validation Error", "detail": [...]}`

## 10. Add pyproject.toml

- [x] 10.1 Create `backend/pyproject.toml` with project metadata, Python version constraint (>=3.10), and all dependencies from `requirements.txt`
- [x] 10.2 Keep `requirements.txt` for Docker compatibility (Dockerfile uses `pip install -r requirements.txt`)
- [x] 10.3 Add `[project.scripts]` entry for `ai-assistant = "main:app"` (optional, for `uvicorn` alternative)

## 11. Frontend React Migration

### 11.1 Project Setup

- [x] 11.1.1 Remove Vue dependencies: `npm uninstall vue @vitejs/plugin-vue vue-tsc`
- [x] 11.1.2 Install React dependencies: `npm install react react-dom && npm install -D @types/react @types/react-dom @vitejs/plugin-react`
- [x] 11.1.3 Update `vite.config.ts` — replace `@vitejs/plugin-vue` with `@vitejs/plugin-react`, keep proxy config unchanged
- [x] 11.1.4 Update `tsconfig.json` / `tsconfig.app.json` — set `"jsx": "react-jsx"`, remove Vue-specific settings
- [x] 11.1.5 Delete all `.vue` files, `HelloWorld.vue`, and Vue-specific type declarations
- [x] 11.1.6 Create `frontend/src/main.tsx` — React 18 `createRoot(document.getElementById('app')!).render(<App />)`
- [x] 11.1.7 Update `index.html` — ensure `<div id="app">` exists (should already from Vue setup)
- [x] 11.1.8 Verify dev server starts: `npm run dev` — Vite starts without errors

### 11.2 Core Components (App → ChatView → MessageList → MessageBubble)

- [x] 11.2.1 Create `src/context/LocaleContext.tsx` — React Context providing `locale` and `t(key)` function; `translations` object ported from `ChatAssistant.vue`
- [x] 11.2.2 Create `src/App.tsx` — session state (`useState` for sessions + currentSessionId), localStorage persistence, CRUD handlers, sidebar/ChatView layout with CSS flex
- [x] 11.2.3 Create `src/components/AppSidebar.tsx` — session list with create/select/rename/delete; mobile hamburger toggle; `useState` for mobile visibility
- [x] 11.2.4 Create `src/components/ChatView.tsx` — message display area, ChatInput, empty-state WelcomeScreen, Agent step panel; SSE reader management with `useRef` (AbortController)
- [x] 11.2.5 Create `src/components/ChatInput.tsx` — text input with Enter-to-send, Shift+Enter for newline, send button; `useState` for input value
- [x] 11.2.6 Create `src/components/MessageList.tsx` — scrollable message container with `useRef` + `useEffect` auto-scroll-to-bottom
- [x] 11.2.7 Create `src/components/MessageBubble.tsx` — user/assistant bubble styles, markdown rendering (basic regex or lightweight lib), Agent step expandable panel, intent badge
- [x] 11.2.8 Create `src/components/WelcomeScreen.tsx` — empty-state view when no messages exist

### 11.3 SSE Streaming Implementation

- [x] 11.3.1 Implement `useChatStream` custom hook or inline logic in ChatView — `fetch` + `ReadableStream` with `AbortController`
- [x] 11.3.2 Parse SSE events: `token` → append to streaming buffer, `step` → show tool call, `step_done` → show tool result, `done` → finalize, `error` → display error
- [x] 11.3.3 Handle stream cancellation: abort fetch on new message send or component unmount
- [x] 11.3.4 Verify typing animation: send "你好" → characters appear one by one, Agent steps visible if tools are called

### 11.4 Knowledge Panel

- [x] 11.4.1 Create `src/components/KnowledgePanel.tsx` — slide-out right panel with toggle button
- [x] 11.4.2 Implement drag-and-drop zone: `onDragOver` / `onDrop` handlers, file type validation (.txt/.pdf/.docx)
- [x] 11.4.3 Implement file upload: `POST /api/documents/upload` with `FormData`, progress state with `useState`
- [x] 11.4.4 Document list: fetch from `GET /api/documents`, display filename/chunks/indexed status, delete button → `DELETE /api/documents/{id}`
- [x] 11.4.5 RAG settings sliders: chunk_size, chunk_overlap, retrieval_k — `useState` synced to `localStorage` (`ai-rag-settings`), save via `POST /api/rag/settings`
- [x] 11.4.6 RAG status display: fetch from `GET /api/rag/status`, show document count + chunk count

### 11.5 Settings Modal

- [x] 11.5.1 Create `src/components/SettingsModal.tsx` — modal overlay with close button, backdrop click to close
- [x] 11.5.2 Create sub-component `ProviderList.tsx` — fetch `GET /api/providers`, separate LLM/Embedding lists, show active status, masked API keys
- [x] 11.5.3 Create sub-component `ProviderForm.tsx` — form for adding custom provider (name, base URL, model, API key); `POST /api/providers`
- [x] 11.5.4 Implement provider activation: click "激活" → `POST /api/providers/{id}/activate` → update provider list state
- [x] 11.5.5 Implement connection test: click "测试连接" → `POST /api/providers/{id}/test` → show success/failure toast
- [x] 11.5.6 Implement custom provider test: `POST /api/providers/test-custom` with form fields

### 11.6 Weather Component

- [x] 11.6.1 Create `src/components/Weather.tsx` — standalone weather query interface; `POST /api/weather` with city or natural language query; display weather info and advice

### 11.7 Styling & Responsive

- [x] 11.7.1 Port all CSS variables and base styles from current `style.css` and component `<style>` blocks to `src/style.css` and component-level `.module.css` files
- [x] 11.7.2 Implement responsive layout: sidebar collapses on mobile (<768px), hamburger button, overlay mode
- [x] 11.7.3 Verify dark mode: `prefers-color-scheme: dark` media query applies correctly in both OS themes
- [x] 11.7.4 Verify all existing visual details match: message bubble shapes, colors, spacing, fonts, transitions

### 11.8 Cleanup

- [x] 11.8.1 Remove `frontend/src/components/HelloWorld.vue` (if still present)
- [x] 11.8.2 Remove any Vue-specific config files (`env.d.ts` with Vue shims, etc.)
- [x] 11.8.3 Verify `npm run build` produces production build without errors
- [x] 11.8.4 Verify frontend Dockerfile still works: `docker compose build frontend`

## 12. Integration Verification

- [x] 12.1 Full server startup: `cd backend && python -m uvicorn main:app --port 8000` — no import errors
- [x] 12.2 Frontend dev server: `cd frontend && npm run dev` — React app loads at `localhost:5173`
- [x] 12.3 Test `/ask` endpoint (non-streaming): `curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"query": "你好"}'` — returns valid response
- [x] 12.4 Test `/ask` endpoint (streaming): `curl -X POST "http://localhost:8000/ask?stream=true" -H "Content-Type: application/json" -d '{"query": "你好"}'` — SSE events received
- [x] 12.5 Test `/sessions` CRUD: create, list, get, rename, delete — all return correct responses
- [x] 12.6 Test `/providers` list: GET `/providers` returns LLM and embedding provider lists
- [x] 12.7 Test `/documents/upload`: upload a .txt file, verify it returns chunks and indexed status
- [x] 12.8 Test `/weather`: POST with `{"query": "北京天气"}` returns weather advice
- [x] 12.9 Test `/rag/status`: GET with session_id returns collection stats
- [x] 12.10 Verify MCP server still works: `cd backend && python -m mcp_server --help`
- [x] 12.11 End-to-end frontend test: create session → send chat message → verify SSE streaming → open knowledge panel → upload document → open settings → switch provider → verify all features work in browser
- [x] 12.12 Test mobile responsive: resize browser to 375px width → sidebar hidden, hamburger visible, chat fills screen
- [x] 12.13 Test i18n: toggle language to English → all UI text changes; refresh page → English persists
- [x] 12.14 Test dark mode: switch OS to dark mode → app renders dark theme; switch to light mode → app renders light theme
- [x] 12.15 Docker compose: `docker compose up --build` — all services start without errors, frontend accessible
- [x] 12.16 Run `lsp_diagnostics` on `backend/` and `frontend/src/` directories — zero errors in changed files

## 13. Final Cleanup

- [x] 13.1 Remove `backend/__pycache__/` directories (gitignored but verify)
- [x] 13.2 Verify `backend/.env` is in `.gitignore`
- [x] 13.3 Delete `frontend/node_modules/` and `frontend/dist/` (gitignored, verify clean)
- [x] 13.4 Run `git status` — verify only intended files are changed
- [x] 13.5 Run `git diff --stat` — confirm line count changes (expected: many deletions from main.py, weather_agent.py, shims, .vue files; additions to new routers/services/schemas, .tsx files)
