"""Weather router — /weather."""

from fastapi import APIRouter, HTTPException

from schemas.weather import WeatherRequest
from tools.weather_tool import WeatherTool

router = APIRouter(tags=["Weather"])


@router.post("/weather")
async def get_weather(request: WeatherRequest):
    try:
        tool = WeatherTool()
        query = request.query or request.city
        if not query:
            raise ValueError("请提供城市名称（city）或自然语言查询（query）")
        result = tool._run(query)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"天气查询失败: {str(e)}")
