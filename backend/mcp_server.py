"""
MCP Server — 将 AI 智能问答助手的 7 个工具以 MCP 协议暴露。

Usage:
    python -m backend.mcp_server                              # stdio (默认，Claude Desktop)
    python -m backend.mcp_server --transport streamable-http --port 8765  # HTTP 远程访问

依赖:
    fastmcp>=3.0    pip install fastmcp
"""

import logging
import os
import sys
from pathlib import Path

# 确保 backend 在 sys.path 中（支持 python -m backend.mcp_server 调用）
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from fastmcp import FastMCP

from model_config import get_openai_client
from tools import get_all_tools
from tools.rag_tool import set_rag_session

logging.basicConfig(level=logging.INFO, format="%(levelname)-7s [mcp] %(message)s")
logger = logging.getLogger("mcp-server")

# ── 加载 .env 配置 ──────────────────────────────────────────
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# ── 初始化（模块级，与 FastAPI 行为一致） ────────────────────
get_openai_client()   # 触发 LLM 客户端初始化（同 text_tools.py 模式）
set_rag_session("mcp")  # MCP 场景使用固定会话，共享知识库

# ── 创建 FastMCP 实例 ───────────────────────────────────────
mcp = FastMCP("ai-assistant")


# ── 工具注册：工厂函数模式，避免 Python 闭包循环陷阱 ─────────
def _register_langchain_tool(lc_tool):
    """将一个 LangChain BaseTool 注册为 MCP 工具。

    FastMCP 3.x 自动将同步函数分派到线程池，因此可以直接定义同步包装器。
    工厂函数确保每个工具拥有独立的闭包作用域。
    """
    def tool_func(input_str: str = "") -> str:
        return lc_tool._run(input_str)

    tool_func.__name__ = lc_tool.name
    tool_func.__doc__ = lc_tool.description

    mcp.tool(name=lc_tool.name, description=lc_tool.description)(tool_func)


for tool in get_all_tools():
    _register_langchain_tool(tool)
    logger.info("已注册 MCP 工具: %s", tool.name)

logger.info("共注册 %d 个工具", len(get_all_tools()))


# ── 入口 ────────────────────────────────────────────────────
if __name__ == "__main__":
    transport = "stdio"
    port = 8765

    # 解析 CLI 参数
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--transport" and i + 1 < len(args):
            transport = args[i + 1]
            i += 2
        elif args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        else:
            i += 1

    # HTTP 传输时的认证警告
    if transport in ("streamable-http", "sse"):
        api_key = os.getenv("MCP_API_KEY", "").strip()
        if not api_key:
            logger.warning(
                "MCP_API_KEY 未在 .env 中设置 — "
                "streamable-http 模式下无认证保护"
            )

    logger.info("启动 MCP Server (transport=%s, port=%s)", transport, port)
    mcp.run(transport=transport, host="0.0.0.0", port=port)
