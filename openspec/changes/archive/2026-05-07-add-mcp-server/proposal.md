## Why

The project currently exposes its 7 AI Agent tools (weather, web search, RAG, summarize, translate, code explain, calculator) only through a FastAPI REST interface. Adding MCP (Model Context Protocol) Server support makes these tools discoverable and callable by any MCP-compatible client (Claude Desktop, Cursor, Continue.dev, etc.), which is a 2026 job market requirement (explicitly listed in multiple AI application developer job postings) and listed as P6 in the project roadmap.

## What Changes

- Add a new `backend/mcp_server.py` that wraps existing LangChain tools as MCP tools using the `fastmcp` library
- Zero modifications to existing tool implementations or the FastAPI application
- Support stdio transport for local use (Claude Desktop integration)
- Support streamable-http transport for remote/team access
- Automatic schema generation from tool type annotations
- RAG tool uses a fixed `"mcp"` session for knowledge base access in MCP context

## Capabilities

### New Capabilities

- `mcp-server`: Expose the 7 existing Agent tools (weather, web search, RAG knowledge base, text summarization, translation, code explanation, calculator) as MCP-compatible tools via stdio and streamable-http transports, with automatic schema generation and no changes to existing code.

### Modified Capabilities

<!-- None - existing code is unchanged -->

## Impact

- **New file**: `backend/mcp_server.py` (~60 lines, thin adapter)
- **New dependency**: `fastmcp` (Python package, community standard for MCP servers)
- **Affected code**: None — existing `backend/tools/`, `backend/agent.py`, `backend/model_config.py`, and `backend/main.py` are untouched
- **Configuration**: Uses existing `.env` for API keys; MCP transport configurable via CLI arguments
- **Claude Desktop**: Requires one-time config entry in `claude_desktop_config.json`
