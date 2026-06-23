## Why

The codebase has accumulated 8+ months of feature additions with no architectural discipline. The backend is a single 761-line `main.py` monolith with duplicate tool classes (two `WeatherTool` implementations), two parallel provider systems coexisting awkwardly, and compatibility shim files that add nothing. The frontend, while partially refactored from a single `ChatAssistant.vue` monolith, is built on Vue 3 — the user has decided to standardize on React for better ecosystem alignment and developer experience. The user has stated the project is beyond incremental fixes — a full restructuring is needed on both sides.

## What Changes

- **BREAKING**: Split `main.py` into FastAPI routers organized by domain (`chat`, `documents`, `sessions`, `providers`, `rag`, `weather`)
- **BREAKING**: Extract business logic from route handlers into service-layer modules (`services/`)
- **BREAKING**: Move Pydantic models from inline definitions to `schemas/` directory
- **BREAKING**: Consolidate `weather_agent.py` into `tools/weather_tool.py` — eliminate the 150-line `city_coords` dict by replacing it with a geocoding approach (LLM-based city→coordinate resolution or free geocoding API), remove duplicate `WeatherTool` class
- **BREAKING**: Remove compatibility shims `session_memory.py` and `session_manager.py` — update all imports to point directly to `session_store.py`
- **BREAKING**: Remove dead code in `provider_manager.py` `get_active_embedding_id()`
- Unify provider initialization path: `provider_manager.py` becomes the **single source of truth**; `model_config.py` reduces to env-reading fallback only
- Standardize async route handlers — all I/O-bound endpoints become `async def`
- Add centralized logging configuration
- Add global exception handlers (unified error response format)
- Replace module-level `DOCUMENTS: list[dict]` with proper session-scoped document tracking via the existing session store
- Ensure `mcp_server.py` imports tools from the canonical `tools/__init__.py` (no duplicate registration logic needed — already correct in current code)
- Fix module-level OpenAI client init in `tools/text_tools.py` — use lazy-init inside `_run()`
- Add `pyproject.toml` for backend with proper dependency management (replace bare `requirements.txt`)
- **BREAKING**: Migrate frontend from Vue 3 to React 18+ with TypeScript — full rewrite of all components while preserving all existing functionality (SSE streaming, multi-session management, RAG knowledge panel, provider settings, i18n, dark mode)

## Capabilities

### New Capabilities
- `backend-service-layer`: Extract all business logic from route handlers into dedicated service modules under `backend/services/` — each service handles one domain (chat, documents, sessions, providers, weather, rag)
- `backend-modular-routers`: Split the monolithic `main.py` into FastAPI APIRouter modules under `backend/routers/` — one router per domain with clear prefix and tag
- `backend-request-schemas`: Extract all Pydantic request/response models into `backend/schemas/` with proper naming and reuse
- `weather-tool-consolidation`: Merge `weather_agent.py` (319 lines) into `tools/weather_tool.py`, replace hardcoded city_coords with LLM-powered geocoding, remove the duplicate `WeatherTool` class
- `backend-error-handling`: Add global FastAPI exception handlers producing consistent `{"error": "...", "detail": "..."}` JSON responses across all endpoints
- `frontend-react-migration`: Rewrite the Vue 3 SPA as a React 18+ TypeScript application — preserve all existing features (SSE chat, session sidebar, knowledge panel, settings modal, i18n, dark mode CSS variables), adopt React ecosystem conventions (functional components, hooks, no class components), use Vite as the build tool (same as current), no CSS framework (maintain CSS variables + dark mode)

### Modified Capabilities
- `multi-provider-config`: Provider initialization is unified — `provider_manager.py` is the sole entry point for LLM/Embedding client creation. `model_config.py` is simplified to a pure config reader (reads `.env`, returns dicts) called only as fallback.
- `rag-document-ingestion`: Document tracking moves from module-level `DOCUMENTS` list to session-store-backed persistence, eliminating the in-memory global.
- `chat-history-persistence`: Session CRUD imports are updated to point to `session_store.py` directly, removing `session_memory.py` and `session_manager.py` shim files.

## Impact

- **Files restructured**: `main.py` (761→~100L), `weather_agent.py` (deleted, ~319L removed), `session_memory.py` (deleted), `session_manager.py` (deleted)
- **New files**: `routers/chat.py`, `routers/documents.py`, `routers/sessions.py`, `routers/providers.py`, `routers/rag.py`, `routers/weather.py`, `services/chat_service.py`, `services/document_service.py`, `services/session_service.py`, `services/provider_service.py`, `services/rag_service.py`, `schemas/chat.py`, `schemas/documents.py`, `schemas/sessions.py`, `schemas/providers.py`, `schemas/rag.py`, `schemas/weather.py`, `pyproject.toml`, `config/logging.py`
- **Models**: `models.py` — no structural changes, DB schema unchanged
- **Tools**: `tools/text_tools.py` — lazy-init fix; `tools/weather_tool.py` — absorbs weather_agent.py; `tools/__init__.py` — updated imports
- **API routes**: ALL route paths remain unchanged — this is a pure internal restructure, zero API surface impact
- **Dependencies**: No new dependencies added; optional `pyproject.toml` replaces `requirements.txt`
- **MCP Server**: `mcp_server.py` — updated import path for `get_all_tools()`, no other changes
- **Docker**: `Dockerfile`, `docker-compose.yml` — updated `CMD` to use new module structure if needed
- **Frontend**: Complete rewrite from Vue 3 to React 18+ — all `.vue` SFC files replaced with `.tsx` components; `main.ts` → React entry point; `vite.config.ts` updated for React plugin; `package.json` dependencies replaced (vue → react, react-dom, @types/react, @types/react-dom); all existing features preserved 1:1
- **Frontend state management**: No Redux, Zustand, or other state library — use React `useState`/`useContext`/`useReducer` (matching the current Vue philosophy of no Pinia/router)
