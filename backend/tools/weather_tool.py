"""
天气查询 Tool - 封装 weather_agent 为 LangChain BaseTool
"""

from langchain.tools import BaseTool

from weather_agent import get_weather_advice_with_focus


class WeatherTool(BaseTool):
    """获取指定城市的天气信息和穿衣建议"""

    name: str = "get_weather"
    description: str = (
        "获取指定城市的当前天气信息，包括温度、湿度、天气状况、风速，以及穿衣和出行建议。"
        "输入应为城市中文或英文名称，如'北京'、'Shanghai'、'合肥'。"
    )

    def _run(self, city: str) -> str:
        try:
            result = get_weather_advice_with_focus(city)
            return result
        except Exception as e:
            return f"天气查询失败: {str(e)}。请检查城市名称是否正确（支持中国 50+ 主要城市）。"

    async def _arun(self, city: str) -> str:
        return self._run(city)
