## 1. Dependency Setup

- [x] 1.1 Add `fastmcp` to `backend/requirements.txt`
- [x] 1.2 Install dependencies and verify import (`python -c "from fastmcp import FastMCP; print('OK')"`)

## 2. Core MCP Server Implementation

- [x] 2.1 Create `backend/mcp_server.py` with FastMCP instance and lifespan that initializes LLM client
- [x] 2.2 Implement `_make_mcp_wrapper(lc_tool)` factory function that bridges LangChain `BaseTool._run()` to async MCP tool via `asyncio.to_thread()`
- [x] 2.3 Register all 7 tools from `get_all_tools()` using the factory pattern with correct name, description, and input schema
- [x] 2.4 Set `set_rag_session("mcp")` at server startup so RAG tool works in MCP context

## 3. Transport Configuration

- [x] 3.1 Implement stdio transport as default (no CLI flags needed)
- [x] 3.2 Add `--transport` CLI argument supporting `stdio` and `streamable-http`
- [x] 3.3 Add `--port` CLI argument for streamable-http (default 8765)
- [x] 3.4 Implement `MCP_API_KEY` Bearer token auth for streamable-http transport, with warning if unset

## 4. Manual Verification

- [x] 4.1 Start stdio server, verify it outputs no errors on startup
- [x] 4.2 Test each of the 7 tools individually via MCP client or Inspector
- [x] 4.3 Configure Claude Desktop (`%APPDATA%\Claude\claude_desktop_config.json`) and verify tools appear in the client
- [x] 4.4 Test end-to-end: ask Claude Desktop a weather question that triggers `get_weather` tool
- [x] 4.5 Test RAG tool: upload a document via FastAPI `POST /documents/upload` with `session_id=mcp`, then query via MCP client
- [x] 4.6 Verify zero modifications to existing source files (`git diff --name-only` shows only `requirements.txt` + new `mcp_server.py`)

## 5. Documentation

- [x] 5.1 Add MCP Server usage section to `README.md` (Claude Desktop config example, CLI flags, how to test)
