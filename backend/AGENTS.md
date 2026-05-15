# backend/ — FastAPI API Server

## OVERVIEW

FastAPI monolith (709-line `main.py`) serving chat, RAG, session, and provider endpoints, with a LangChain 1.x Tool-Calling Agent and dual-mode storage.

## FILE MAP

| File | Why it exists |
|------|---------------|
| `main.py` (709L) | ALL routes live here: `/ask` (chat+SSE), `/documents/*` (RAG upload/list/delete), `/sessions/*` (CRUD), `/rag/*` (status/settings), `/providers` (dynamic switch), `/weather`, `/models/*`, legacy `/intent` handlers. No `routers/` directory. |
| `agent.py` | Creates LangChain 1.x Tool-Calling Agent via `create_agent()`. Exports `run_agent()` (sync, `{response, steps}`) and `run_agent_stream()` (SSE-generator). Config: 5 max iterations, 30s timeout. |
| `model_config.py` | **Static** provider config from `.env` (`LLM_PROVIDER`, `ZHIPU_API_KEY`). Returns `get_openai_client()` and `get_langchain_llm()`. Used by legacy code + fallback path. |
| `provider_manager.py` | **Dynamic** provider switching from DB (`model_providers` table). Singleton via `get_provider_manager()`. Returns clients/configs for active LLM/Embedding. **Takes precedence over `model_config.py` when available.** |
| `database.py` | Dual-mode MySQL engine: async aiomysql when `USE_MYSQL=true`, else in-memory dict. Check `is_mysql_enabled()`. Contains hardcoded fallback credentials (line 19). |
| `models.py` | SQLAlchemy ORM: `sessions` table (metadata) and `messages` table (user/assistant with foreign key CASCADE). |
| `session_store.py` | **Canonical** session module (454L). Dual-mode: MySQL via async ORM or in-memory dict. Handles messages, context windows, session CRUD, user preferences. |
| `session_memory.py` | Compatibility shim — re-exports from `session_store`. Import still works but adds no value. |
| `session_manager.py` | Compatibility shim — re-exports from `session_store`. Same as above. |
| `encryption.py` | Fernet symmetric encryption for API keys in DB. Auto-generates `FERNET_KEY` into `.env` on first run. Exports `encrypt_key()`, `decrypt_key()`, `mask_key()`. |
| `weather_agent.py` | Standalone WeatherTool with `city_coords` dict + `get_weather_advice_with_focus()`. Separate from `tools/weather_tool.py` which wraps it. Module-level LLM init (anti-pattern). |
| `mcp_server.py` | Re-registers all 7 tools via FastMCP. Supports stdio (Claude Desktop) and streamable-http. No auth enforcement — only warns if `MCP_API_KEY` unset. |
| `tools/` | 7 LangChain BaseTool subclasses. See `tools/AGENTS.md` for per-tool details. |

## WHERE TO LOOK

| Task | File(s) |
|------|---------|
| Add API route | `main.py` — append route function, no separate router module |
| Change Agent behavior | `agent.py` for loop config; `tools/` for tool logic |
| Switch LLM provider | `.env` for static; `provider_manager.py` for dynamic DB-backed |
| Add session storage field | `session_store.py` + `models.py` (if MySQL) |
| Change RAG chunking/retrieval | `tools/rag_tool.py` |
| Modify MCP tool exposure | `mcp_server.py` — registers tools independently of `tools/__init__.py` |
| Debug SSE streaming | `main.py` `/ask?stream=true` handler → `agent.py` `run_agent_stream()` |

## INTERNAL PATTERNS

**Provider init chain**: `.env` → `model_config.py` (static) AND/OR DB → `provider_manager.py` (dynamic). Both coexist; `provider_manager` wins when DB has active provider. `agent.py` always reads from `provider_manager` first, falls back to `model_config.py`.

**Session dual-mode**: `session_store.py` checks `is_mysql_enabled()` at runtime. MySQL path uses async ORM (`async_sessionmaker`); in-memory path uses plain `dict`. All public functions (`get_history`, `add_message`, `create_session`, etc.) return the same interface regardless of mode.

**Route organization in main.py**: No routers. All endpoints are `@app.{method}()` on the FastAPI instance. SSE uses `StreamingResponse` with manual `event: type\ndata: {json}\n\n` formatting. CORS configured via explicit allowlist (not wildcard).

**Tool error contract**: Every tool returns error strings. Never raise exceptions. Pattern: `return f"失败: {str(e)}"`.

## ANTI-PATTERNS

- **Module-level LLM init**: `weather_agent.py:13` and `tools/text_tools.py:9` call `get_langchain_llm()` / `get_openai_client()` at import time. Provider hot-switching silently fails for these. Use lazy-init inside `_run()`.
- **Hardcoded DB credentials**: `database.py:19` fallback contains live credentials. Use `.env` only.
- **Import from shim files**: `from session_memory import ...` or `from session_manager import ...` still works but adds unnecessary indirection. Import directly from `session_store`.
- **Dead code in provider_manager**: `get_active_embedding_id()` (line 54-59) has unreachable code after `return` on line 56.
- **Duplicate tool registration**: `mcp_server.py` registers tools independently from `tools/__init__.py`. Adding a tool requires changes in both places.
- **No test framework**: `test_mcp.py` is standalone. No pytest/vitest equivalents exist. Manual testing only.
