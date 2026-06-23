## Context

The backend is a FastAPI monolith (`main.py`, 761 lines) with all routes, business logic, and inline Pydantic models in a single file. The codebase has grown organically since its initial scaffold and now suffers from:

- **No separation of concerns**: Route handlers contain business logic, database queries, file I/O, and external API calls interleaved
- **Duplicate code**: Two `WeatherTool` classes exist (`weather_agent.py:24` and `tools/weather_tool.py:10`), tool registration happens in both `tools/__init__.py` and `mcp_server.py`
- **Redundant files**: `session_memory.py` (20L) and `session_manager.py` (17L) are pure re-export shims
- **Parallel provider systems**: `model_config.py` (static, env-based) and `provider_manager.py` (dynamic, DB-backed) coexisting with inconsistent precedence rules
- **Module-level globals**: `DOCUMENTS: list[dict] = []` in `main.py`, `client` init at import time in `text_tools.py`
- **No error handling middleware**: Exceptions bubble up as raw FastAPI HTTPException or 500s

The frontend was already partially refactored (split from `ChatAssistant.vue` monolith into `AppSidebar.vue`, `ChatView.vue`, `MessageBubble.vue`, etc.), but the backend has not kept pace.

**Constraints:**
- Zero API surface change — all route paths, request/response shapes, SSE event format remain identical
- DB schema (`models.py`) remains unchanged
- No new backend dependencies (optional: `pyproject.toml` standardizes existing deps)
- Must work in both MySQL and in-memory modes (per existing `session_store.py` dual-mode)
- Backward-compatible: existing `.env` files, Docker setup all continue working
- Frontend rewrite to React: preserve 100% of existing functionality, UI, and UX — users see no difference

## Goals / Non-Goals

**Goals:**
1. Split `main.py` into FastAPI APIRouters organized by domain — one router per concern
2. Extract business logic into service-layer modules that routers delegate to
3. Centralize Pydantic models in `schemas/` with clear naming
4. Consolidate weather logic into a single `tools/weather_tool.py` — eliminate `weather_agent.py`
5. Remove `session_memory.py` and `session_manager.py` shims
6. Unify provider initialization — `provider_manager.py` as sole entry point
7. Fix module-level init anti-patterns (lazy-init in `_run()`)
8. Add global exception handlers with consistent JSON error format
9. Replace module-level `DOCUMENTS` list with session-store-backed document tracking
10. Add centralized logging configuration
11. Add `pyproject.toml` for proper Python project metadata
12. **Migrate frontend from Vue 3 to React 18+** with TypeScript, preserving all existing features exactly

**Non-Goals:**
- No DB schema changes (models.py untouched structurally)
- No new features or behavioral changes to tools
- No MCP protocol changes
- No test framework setup (still manual testing)
- No CI/CD pipeline
- No authentication/authorization system
- No API versioning
- No CSS framework or component library (keep CSS variables + dark mode)
- No state management library (Redux, Zustand, etc.) — React `useState`/`useContext`/`useReducer` only, mirroring current Vue philosophy of no Pinia

## Decisions

### D1: Router organization — domain-based vs. resource-based

**Decision:** Domain-based routers matching existing API groups.

```
routers/
├── __init__.py
├── chat.py          # POST /ask, GET /history, POST /history/clear
├── documents.py     # POST /documents/upload, GET /documents, DELETE /documents, DELETE /documents/{id}
├── sessions.py      # GET/POST /sessions, GET/PATCH/DELETE /sessions/{id}, GET /sessions/{id}/history
├── providers.py     # GET/POST /providers, PUT/DELETE /providers/{id}, POST /providers/{id}/activate, POST /providers/{id}/test, POST /providers/test-custom
├── rag.py           # GET /rag/status, GET/POST /rag/settings
├── weather.py       # POST /weather
└── preferences.py   # POST/GET/DELETE /preferences
```

**Rationale:** Domain-based grouping matches the existing API surface exactly. Each router maps to a frontend feature area. Resource-based (e.g., `/api/v1/`) would add versioning complexity with zero benefit for a single-consumer SPA.

**Alternative considered:** Flat routers in `routers/` but keeping all in one `api.py`. Rejected — even a few routers benefit from separation when each is 50-100 lines.

### D2: Service layer pattern

**Decision:** Simple function-based service modules, no classes or dependency injection.

```python
# services/chat_service.py
async def handle_chat_query(query: str, session_id: str, stream: bool, db: AsyncSession) -> dict | StreamingResponse:
    ...

# services/document_service.py
async def upload_document(file: UploadFile) -> dict:
    ...
def list_documents() -> list[dict]:
    ...
```

Each service module is a collection of async functions. The router handles HTTP concerns (parsing, status codes, response formatting); the service handles business logic.

**Rationale:** The codebase already uses functional patterns (e.g., `session_store.py` functions). Adding a DI framework or class-based services would be over-engineering for ~10 service functions. Functions are trivially testable in isolation when a test framework is added later.

**Alternative considered:** Class-based services with `__init__` injecting dependencies. Rejected — adds boilerplate with no benefit for this scale. Functions that accept `db: AsyncSession` as a parameter are already dependency-injectable via FastAPI's `Depends`.

### D3: Provider unification

**Decision:** `provider_manager.py` becomes the single entry point. `model_config.py` reduces to `read_provider_config()` that returns a `dict` of env-based defaults, called only as fallback when DB has no active provider.

**Current state (problem):**
```
agent.py → provider_manager (priority) → model_config (fallback)
text_tools.py → provider_manager (line 7) AND model_config (line 8)
weather_agent.py → provider_manager → model_config (fallback)
main.py → provider_manager via _get_client()
```

**Target state:**
```
ALL consumers → provider_manager.get_active_llm_client()
                      └── DB active provider? → use it
                      └── No DB? → model_config.read_provider_config() as fallback
```

`model_config.py` no longer exports `get_openai_client()` or `get_langchain_llm()` — it exports `read_llm_config() -> dict` and `read_embedding_config() -> dict`.

### D4: Weather tool consolidation

**Decision:** Merge `weather_agent.py` logic into `tools/weather_tool.py`. Replace the 150-line `city_coords` dict with LLM-based geocoding.

The `WeatherTool._run()` will:
1. Accept a natural language query (not just city name)
2. Use the active LLM to extract city name from the query
3. Use the active LLM to resolve city → latitude/longitude coordinates (since LLMs know major city coordinates)
4. Call Open-Meteo API with the resolved coordinates
5. Use the active LLM to generate advice from the weather data

This eliminates the hardcoded city list entirely, supporting any city the LLM knows coordinates for.

The old `city_coords` dict (~150 lines), `extract_city_from_query()`, `extract_user_focus()`, and the standalone `WeatherTool` class in `weather_agent.py` are all removed.

`weather_agent.py` is **deleted**. The two public functions (`get_weather_advice`, `get_weather_advice_with_focus`) are reimplemented in the consolidated `WeatherTool`.

### D5: Document tracking

**Decision:** Replace module-level `DOCUMENTS: list[dict]` with a `document_registry` dict in `session_store.py` (for in-memory mode) and leverage the existing `documents` upload directory as the source of truth.

For MySQL mode, document metadata is tracked via the session (documents are associated with a session_id). For in-memory mode, a simple `_document_registry: dict[str, list[dict]]` maps session_id → list of document metadata.

The RAG vector store already persists independently via ChromaDB, so document metadata just needs to survive server restarts in MySQL mode and be available per-session in memory mode.

### D6: Schema organization

**Decision:** One schema file per domain, mirroring the router structure.

```
schemas/
├── __init__.py
├── chat.py        # QueryRequest, chat response models
├── documents.py   # document upload/response models
├── sessions.py    # CreateSessionRequest, UpdateSessionRequest, SessionResponse
├── providers.py   # ProviderCreateRequest, ProviderUpdateRequest, ProviderTestRequest, etc.
├── rag.py         # RagSettingsRequest, RagStatusResponse
├── weather.py     # WeatherRequest
└── preferences.py # PreferencesRequest
```

All models use Pydantic v2 `BaseModel`. Naming convention: `{Domain}{Action}Request` / `{Domain}{Action}Response`.

### D7: Frontend React migration — 1:1 feature parity

**Decision:** Rewrite all Vue 3 components as React 18+ functional components with TypeScript. Preserve every feature, interaction, and visual detail exactly — the app should be indistinguishable from the current version to end users.

**Component mapping (Vue → React):**

| Vue Component | React Equivalent | Lines (approx.) |
|---|---|---|
| `App.vue` (104L) | `App.tsx` | Session state, sidebar/ChatView layout |
| `AppSidebar.vue` | `AppSidebar.tsx` | Session list, create/rename/delete |
| `ChatView.vue` | `ChatView.tsx` | Message display area + ChatInput |
| `ChatInput.vue` | `ChatInput.tsx` | Text input + send button |
| `MessageList.vue` | `MessageList.tsx` | Scrollable message container |
| `MessageBubble.vue` | `MessageBubble.tsx` | Single message (user/assistant), markdown, Agent steps |
| `WelcomeScreen.vue` | `WelcomeScreen.tsx` | Empty-state welcome view |
| `KnowledgePanel.vue` (768L) | `KnowledgePanel.tsx` | Drag-drop upload, progress, doc list, RAG sliders |
| `SettingsModal.vue` (1232L) | `SettingsModal.tsx` | Provider switching, RAG params |
| `Weather.vue` (87L) | `Weather.tsx` | Standalone weather component |

**State management strategy:**
- **No external state library** — `useState` for local state, `useContext` for cross-cutting concerns (locale, current session)
- Session list and current session ID stored in `App.tsx` via `useState`, persisted to `localStorage` (same keys: `ai-chat-sessions`, `ai-chat-current-session`)
- Locale (`zh`/`en`) via React Context (`LocaleContext`)
- SSE streaming state via `useRef` (AbortController, reader reference) + `useState` (streaming text buffer)
- RAG settings via `useState` synced to `localStorage` (`ai-rag-settings`)

**SSE handling:**
- Same manual `fetch` + `ReadableStream` approach (not `EventSource`)
- Parse `event: type\ndata: {json}\n\n` format identically
- Events: `token` (append to buffer), `step` (show tool call), `step_done` (show tool result), `done` (finalize), `error` (display error)

**i18n approach:**
- Same manual `translations` object pattern (no `react-i18next` or similar)
- `LocaleContext` provides current locale and `t(key)` function
- Toggle button in chat header

**Styling:**
- CSS variables + `prefers-color-scheme: dark` — zero changes to the styling approach
- All existing CSS moved to component-level `.module.css` files or a shared `style.css`
- No Tailwind, no CSS-in-JS, no component library

**Build tool:**
- Keep Vite — switch from `@vitejs/plugin-vue` to `@vitejs/plugin-react`
- `vite.config.ts` updated: proxy `/api` → `http://backend:8000` (unchanged)

**Dependencies removed:** `vue`, `@vitejs/plugin-vue`, `vue-tsc`
**Dependencies added:** `react`, `react-dom`, `@types/react`, `@types/react-dom`, `@vitejs/plugin-react`

**Rationale:** React has a larger ecosystem, more hiring pool alignment, and the user explicitly requested it. The app's architecture (no router, no state library) makes the migration straightforward — components are self-contained and data flow is unidirectional. The SSE parser, localStorage keys, CSS variables, and API calls are framework-agnostic and transfer directly.

**Alternative considered:** Incremental migration via micro-frontend (mounting React components inside Vue). Rejected — adds complexity (two build pipelines, interop layer) for a small SPA. Full rewrite is simpler and produces a cleaner result.

## Risks / Trade-offs

- **[Risk] LLM-based geocoding may produce incorrect coordinates for obscure cities**
  → Mitigation: Retain a small hardcoded fallback dict of the 10 most common cities. If the LLM returns coordinates that produce an Open-Meteo error, fall back to the dict. Also validate that resolved coordinates are within reasonable bounds (lat: -90 to 90, lon: -180 to 180).

- **[Risk] Router split could break import paths that other files depend on**
  → Mitigation: The only external consumers are `mcp_server.py` and `main.py`. `agent.py` and `tools/` have no dependency on route-level code. Audit all imports before deleting any file.

- **[Risk] Provider unification could break the fallback path for users who only use `.env` config**
  → Mitigation: `provider_manager.py` already has a `_reload_llm_sync()` fallback that reads from `model_config`. The change is that `model_config` exports dicts instead of client instances, but `provider_manager` constructs clients from those dicts — functionally identical.

- **[Trade-off] Service layer adds indirection for simple endpoints**
  → Accepted. The trade-off is worthwhile for testability and separation of concerns. Simple endpoints (e.g., `GET /rag/status`) can have thin service functions that are nearly pass-through.

- **[Trade-off] pyproject.toml replaces requirements.txt**
  → `requirements.txt` is kept as a symlink or copy for Docker compatibility. `pyproject.toml` becomes the canonical dependency source.

- **[Risk] React migration could introduce subtle behavioral differences**
  → Mitigation: Every component is verified against its Vue counterpart before marking complete. SSE parsing logic is ported line-for-line. localStorage keys and API calls are identical. The verification task group (11.x) includes explicit checks for each feature.

- **[Risk] Large KnowledgePanel (768L) and SettingsModal (1232L) are complex to rewrite**
  → Mitigation: These are the highest-risk components. They are broken into smaller sub-components during migration (e.g., `ProviderList`, `ProviderForm`, `RagSliders`) rather than rewritten as single monoliths.

- **[Trade-off] Two framework migrations in one change (backend + frontend)**
  → Accepted. The user explicitly requested both. The implementation is structured so backend and frontend can be worked on in parallel — they share only the API contract which is unchanged.

## Open Questions

1. **Should we add a `config/` directory for logging and app configuration?** — Yes, this is included. `config/logging.py` for centralized logging setup, `config/settings.py` for env-based settings if needed later.
2. **Should the `weather_agent.py` city_coords be completely removed or archived somewhere?** — Removed. The data is trivially reproducible (Open-Meteo + LLM can resolve any city).
3. **Should the Dockerfile CMD be updated to use the new module path?** — Yes, but only if the entry point changes. Currently `uvicorn main:app` will still work since `main.py` remains the app factory, just slimmed down to router registration.
4. **React version?** — React 18.x (latest stable). React 19 is released but 18.x has broader ecosystem compatibility. Vite + React 18 is well-tested.
5. **Should KnowledgePanel and SettingsModal be split into smaller components during migration?** — Yes. The current Vue monoliths (768L and 1232L) should become 3-5 focused React components each. This is noted in the tasks.
