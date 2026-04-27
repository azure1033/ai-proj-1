"""
网页搜索 Tool - 支持 Tavily / DuckDuckGo
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.tools import BaseTool

# 加载项目根目录 .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()


class WebSearchTool(BaseTool):
    """搜索互联网获取最新信息"""

    name: str = "web_search"
    description: str = (
        "搜索互联网获取最新信息。输入搜索关键词，返回相关网页的标题、摘要和链接。"
        "用于获取实时新闻、最新数据、事实查询等。"
    )

    def _run(self, query: str) -> str:
        if TAVILY_API_KEY:
            result = self._search_tavily(query)
            # Tavily 失败 → 自动降级到 DuckDuckGo
            if result.startswith("[服务提示:"):
                fallback = self._search_duckduckgo(query)
                if not fallback.startswith("[服务提示:"):
                    return fallback
            return result
        else:
            return self._search_duckduckgo(query)

    async def _arun(self, query: str) -> str:
        return self._run(query)

    @staticmethod
    def _search_tavily(query: str) -> str:
        """使用 Tavily Search API"""
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=TAVILY_API_KEY)
            response = client.search(query, max_results=5)
            results = response.get("results", [])
            if not results:
                return f"未找到关于 '{query}' 的相关结果。"
            lines = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "无标题")
                content = r.get("content", "")
                url = r.get("url", "")
                lines.append(f"{i}. {title}\n   {content[:200]}...\n   {url}")
            return "\n\n".join(lines)
        except ImportError:
            return "[服务提示: Tavily 搜索库未安装，请使用 DuckDuckGo 备选方案]"
        except Exception as e:
            return f"[服务提示: 搜索服务暂时不可用]"

    @staticmethod
    def _search_duckduckgo(query: str) -> str:
        """使用 DuckDuckGo 搜索（免费，无需 API Key）"""
        try:
            from ddgs import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=5):
                    results.append(r)
            if not results:
                return f"未找到关于 '{query}' 的相关结果。"
            lines = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "无标题")
                body = r.get("body", "")
                href = r.get("href", "")
                lines.append(f"{i}. {title}\n   {body[:200]}...\n   {href}")
            return "\n\n".join(lines)
        except ImportError:
            return "[服务提示: 搜索服务暂未配置，请基于已有知识回答]"
        except Exception as e:
            return f"[服务提示: 搜索服务暂时不可用]"
