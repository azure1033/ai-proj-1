## Context

The project has 7 LangChain `BaseTool` implementations (weather, web search, RAG, summarize, translate, code explain, calculator) registered via `tools/__init__.py::get_all_tools()`. These are currently only accessible through the LangChain Agent in `agent.py`, which is invoked by the FastAPI `/ask` endpoint.

MCP (Model Context Protocol) has become the de facto standard for tool exposure in the AI ecosystem (97M+ monthly downloads, 10,000+ active servers). Multiple 2026 job postings explicitly require MCP integration experience. The project roadmap already lists MCP Server as P6.

All 7 tools share an identical interface (`(str) -> str` via `_run()`), making a thin adapter layer feasible with zero changes to existing code.

## Goals / Non-Goals

**Goals:**
- Expose all 7 existing tools as MCP-compatible tools without modifying any existing source files
- Support stdio transport for local integration (Claude Desktop, Cursor, Continue.dev)
- Support streamable-http transport for remote/team access
- Auto-generate MCP tool schemas from LangChain tool metadata (name, description)
- Reuse existing `.env`-based API key and provider configuration
- RAG tool works in MCP context with a fixed session identifier

**Non-Goals:**
- No changes to existing tool implementations, agent logic, or FastAPI endpoints
- No MCP Client implementation (this change is Server only)
- No MCP Resources or Prompts (tools only, matching the existing capability set)
- No OAuth or complex authentication (API key via env var for HTTP transport only)
- No tool discovery or dynamic registration beyond the static tool set

## Decisions

### 1. SDK: `fastmcp` standalone (v3.x) over official `mcp` SDK

**Rationale**: The standalone `fastmcp` package (PrefectHQ, v3.x) is used by ~70% of production MCP servers. It provides decorator-based tool registration, automatic type-hint-to-JSON-Schema generation, built-in `asyncio.to_thread` for sync tool bridging, and testing utilities. The official `mcp` SDK's built-in FastMCP is frozen at v1-era capabilities and lacks these features.

**Alternatives considered**:
- `lc2mcp` (71★ library): Handles LangChain → MCP conversion automatically, but adds a dependency for logic we can write in ~15 lines since all tools share a uniform interface.
- Official `mcp` low-level `Server` API: Maximum control but requires manual JSON Schema for every tool — excessive for 7 simple string-in/string-out tools.
- Official `mcp.server.fastmcp.FastMCP` (v1): Works but lacks async bridging and testing utilities.

### 2. Architecture: Thin adapter in a single file

**Rationale**: `backend/mcp_server.py` imports `get_all_tools()` and wraps each tool with the `@mcp.tool` decorator. This is a pure adapter layer — no new abstractions, no shared state with the FastAPI app.

**Structure**:
```
backend/mcp_server.py   ← NEW (single file, ~60 lines)
backend/tools/          ← UNCHANGED
backend/model_config.py ← UNCHANGED
```

### 3. Tool wrapping: Factory function pattern to avoid closure bugs

Python closures in loops capture variables by reference. A factory function (`_make_mcp_wrapper(lc_tool)`) creates a unique closure per tool, ensuring each MCP tool calls the correct LangChain tool instance.

Each wrapper:
- Takes a single `input_str: str` parameter
- Uses `asyncio.to_thread(tool._run, input_str)` for non-blocking execution
- Returns the tool's string output directly

### 4. Transport: stdio default, streamable-http via CLI flag

Default to stdio (zero-config for Claude Desktop). Streamable-http available via `--transport streamable-http --port 8765`. Both use the same tool set. Streamable-http enforces `MCP_API_KEY` via Bearer token if set.

### 5. RAG session: Fixed `"mcp"` session ID

The `RAGSearchTool` reads `session_id` from `contextvars`. In MCP context, there is no FastAPI request to set this. Before wrapping the RAG tool, `set_rag_session("mcp")` is called once at server startup, giving all MCP RAG queries a shared knowledge base. This is appropriate since MCP Server is typically single-user.

### 6. Error handling: Graceful degradation

Tool errors are caught at the wrapper level and returned as error strings (matching the existing tool pattern of returning error strings rather than raising exceptions). This prevents MCP protocol errors from propagating to the client.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| `fastmcp` prints startup banner to stdout, which can break JSON-RPC parsers in strict clients | Use `mcp.run(transport="stdio", show_banner=False)` if available; otherwise accept that Claude Desktop handles this correctly |
| Sync tools block the event loop if not properly bridged | All wrappers use `asyncio.to_thread()` which runs in a thread pool |
| `text_tools.py` initializes `client = get_openai_client()` at module import time | Works correctly — `mcp_server.py` imports trigger the same module initialization as FastAPI |
| RAG tool's `contextvars` dependency on session context | Mitigated by calling `set_rag_session("mcp")` at server startup |
| `fastmcp` has a heavier dependency footprint than official SDK | Acceptable trade-off for built-in features (auth, testing, schema generation) |

## Open Questions

1. **Claude Desktop config path**: Windows path for `claude_desktop_config.json` — verified at `%APPDATA%\Claude\claude_desktop_config.json`. Document this in the implementation.
2. **MCP_API_KEY for streamable-http**: Should we require it or just warn? Decision: warn if unset, allow connection. This matches elasticsearch-mcp-server's production pattern.
