"""
Agent 工具集
"""

from tools.weather_tool import WeatherTool
from tools.web_search import WebSearchTool
from tools.text_tools import SummarizeTool, TranslateTool, ExplainCodeTool
from tools.calculator import CalculatorTool
from tools.rag_tool import get_rag_tool


def get_all_tools() -> list:
    """返回所有可用工具，RAG 工具始终存在于列表中"""
    return [
        WeatherTool(),
        WebSearchTool(),
        SummarizeTool(),
        TranslateTool(),
        ExplainCodeTool(),
        CalculatorTool(),
        get_rag_tool(),
    ]
