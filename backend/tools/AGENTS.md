# tools/ — Agent Tool Suite

## OVERVIEW
7 LangChain BaseTool subclasses surfaced via `get_all_tools()` to `agent.py` and `mcp_server.py`.

## TOOL REGISTRY
`__init__.py::get_all_tools()` returns a flat `list` of instantiated tools. RAG uses `get_rag_tool()` factory; the other 6 are direct constructors. To add a tool: subclass BaseTool, import it here, append to the list. No registration beyond this file.

## TOOL LIST

| Tool | File | Input → Output | Key Dependency |
|------|------|----------------|----------------|
| `WeatherTool` | `weather_tool.py` | city name → weather + advice | `weather_agent.get_weather_advice_with_focus()` |
| `WebSearchTool` | `web_search.py` | query string → top-5 results | Tavily API → DuckDuckGo fallback |
| `RAGSearchTool` | `rag_tool.py` | question → top-k chunks | ChromaDB, `contextvars` session isolation |
| `SummarizeTool` | `text_tools.py` | raw text → LLM summary | shared `client` (line 9) |
| `TranslateTool` | `text_tools.py` | raw text → CN translation | shared `client`, EN→ZH only |
| `ExplainCodeTool` | `text_tools.py` | code snippet → explanation | shared `client` |
| `CalculatorTool` | `calculator.py` | math expr → numeric result | regex whitelist + restricted `eval()` |

## TOOL CONTRACT
Every tool subclasses `BaseTool` with:
- `name: str` — agent-facing identifier
- `description: str` — LLM-readable usage guidance
- `_run(self, input: str) -> str` — synchronous path
- `_arun(self, input: str) -> str` — async (delegates to `_run`)

**Error rule**: Return error strings. Never raise. Pattern: `return f"工具名失败: {str(e)}"`.

## ANTI-PATTERNS
- **`text_tools.py:9`** — `client = get_openai_client()` at module level. Lazy-init inside `_run()` instead, or provider hot-switching silently fails.
- **Duplicate WeatherTool** — `weather_agent.py` carries a standalone WeatherTool class with `city_coords`. The canonical version is `tools/weather_tool.py`. The duplicate (outside `tools/`) should be removed.
