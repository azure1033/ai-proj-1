# mcp-server

## Purpose

Expose the AI Assistant's 7 LangChain tools as MCP (Model Context Protocol) compatible tools, enabling integration with MCP clients such as Claude Desktop, Cursor, and Continue.dev. The MCP Server is a thin adapter layer that requires zero modifications to existing tool implementations.

## Requirements

### Requirement: MCP Server exposes all existing tools

The system SHALL expose all 7 LangChain tools (get_weather, web_search, search_knowledge_base, summarize_text, translate_text, explain_code, calculator) as MCP-compatible tools via a single `backend/mcp_server.py` entry point.

#### Scenario: Client discovers available tools

- **WHEN** an MCP client connects to the server
- **THEN** the server returns a tool list containing exactly 7 tools with names matching the LangChain tool names
- **AND** each tool's description matches the LangChain tool's description field

#### Scenario: Client calls a weather tool

- **WHEN** an MCP client calls `get_weather` with input `"北京"`
- **THEN** the server returns weather information for Beijing in the same format as the existing `WeatherTool._run()` output

#### Scenario: Client calls a tool that fails gracefully

- **WHEN** an MCP client calls any tool and the underlying `_run()` method returns an error string
- **THEN** the server returns that error string as the tool result without raising an MCP protocol error

### Requirement: Zero modification to existing code

The MCP Server implementation SHALL NOT modify any existing source files in the `backend/` directory. All adapter logic MUST be contained in the new `backend/mcp_server.py` file.

#### Scenario: Existing tools remain unchanged

- **WHEN** the MCP Server is added to the project
- **THEN** all files under `backend/tools/`, `backend/agent.py`, `backend/model_config.py`, and `backend/main.py` remain byte-identical to their pre-MCP state

### Requirement: stdio transport support

The MCP Server SHALL support stdio transport for local integration with desktop MCP clients.

#### Scenario: Server starts with stdio transport

- **WHEN** the server is launched with `python -m backend.mcp_server` (no transport flags)
- **THEN** the server listens on stdio and responds to MCP JSON-RPC messages
- **AND** the server is compatible with Claude Desktop's MCP client configuration

### Requirement: streamable-http transport support

The MCP Server SHALL support streamable-http transport for remote access when launched with the appropriate CLI flag.

#### Scenario: Server starts with streamable-http transport

- **WHEN** the server is launched with `python -m backend.mcp_server --transport streamable-http --port 8765`
- **THEN** the server listens on HTTP at the specified port and accepts MCP requests

#### Scenario: streamable-http with API key enforcement

- **WHEN** `MCP_API_KEY` is set in `.env` and the server uses streamable-http transport
- **THEN** requests without a valid Bearer token are rejected
- **AND** requests with the correct Bearer token are accepted

#### Scenario: streamable-http without API key

- **WHEN** `MCP_API_KEY` is NOT set in `.env` and the server uses streamable-http transport
- **THEN** a warning is logged and all requests are accepted without authentication

### Requirement: RAG tool works in MCP context

The RAG knowledge base tool (`search_knowledge_base`) SHALL function correctly when called via MCP, using a fixed session identifier `"mcp"`.

#### Scenario: RAG tool called without prior session setup

- **WHEN** an MCP client calls `search_knowledge_base` with a query
- **THEN** the tool uses the `"mcp"` session's ChromaDB collection for vector search
- **AND** the result matches what would be returned from the FastAPI endpoint with `session_id="mcp"`

#### Scenario: RAG tool called with empty knowledge base

- **WHEN** an MCP client calls `search_knowledge_base` and no documents have been uploaded to the `"mcp"` session
- **THEN** the tool returns the existing friendly message `"当前知识库中暂无文档。请先上传文档后再查询。"`

### Requirement: Configuration via existing .env file

The MCP Server SHALL reuse the project's existing `.env` file for all LLM provider and API key configuration.

#### Scenario: Server starts with zhipu provider

- **WHEN** `.env` sets `LLM_PROVIDER=zhipu` and `ZHIPU_API_KEY` is valid
- **THEN** tools that require LLM calls (summarize_text, translate_text, explain_code, get_weather) function correctly

#### Scenario: Server starts with ollama provider

- **WHEN** `.env` sets `LLM_PROVIDER=ollama` and Ollama is running locally
- **THEN** all tools function correctly using the local Ollama model
