"""
天气查询 Tool — 支持自然语言输入，LLM 提取城市 + 地理编码 + Open-Meteo 数据 + LLM 建议生成。
"""
import json
import logging
import re
from typing import ClassVar, Dict, Tuple

import requests
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 懒加载 LLM（优先 DB 动态配置，回退 model_config）
# ---------------------------------------------------------------------------

def _get_llm():
    """懒加载 LLM（每次调用时动态获取，支持 Provider 热切换）"""
    try:
        from provider_manager import get_provider_manager
        pm = get_provider_manager()
        llm = pm.get_active_llm_config()
        if llm is not None:
            return llm
    except Exception:
        pass
    from model_config import read_llm_config
    from langchain_openai import ChatOpenAI
    cfg = read_llm_config()
    return ChatOpenAI(
        model=cfg["model"],
        openai_api_key=cfg["api_key"],
        openai_api_base=cfg["base_url"],
        temperature=0.7,
    )


# ---------------------------------------------------------------------------
# 天气描述码 → 中文
# ---------------------------------------------------------------------------

WEATHER_DESCRIPTIONS: Dict[int, str] = {
    0: "晴朗", 1: "大部分晴朗", 2: "部分多云", 3: "多云",
    45: "雾", 48: "雾",
    51: "小雨", 53: "中雨", 55: "大雨",
    56: "小冻雨", 57: "大冻雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    66: "小冻雨", 67: "大冻雨",
    71: "小雪", 73: "中雪", 75: "大雪", 77: "雪粒",
    80: "小阵雨", 81: "中阵雨", 82: "大阵雨",
    85: "小阵雪", 86: "大阵雪",
    95: "雷暴", 96: "雷暴伴小冰雹", 99: "雷暴伴大冰雹",
}

# ---------------------------------------------------------------------------
# 建议 Prompt
# ---------------------------------------------------------------------------

WEATHER_PROMPT = PromptTemplate.from_template("""
你是一个智能天气助手。基于以下天气信息，给出实用的生活建议。

天气信息: {weather_info}

用户关注点：{user_focus}

根据用户的关注点，重点提供相关建议：
1. 针对用户提到的问题给出明确答复
2. 补充一些用户没提到但有用的建议（作为额外提示）
3. 用友好的语气回复

格式：先直接回答用户的问题，然后说"此外，我还建议..."来补充其他建议。
""")


# ---------------------------------------------------------------------------
# WeatherTool
# ---------------------------------------------------------------------------

class WeatherTool(BaseTool):
    """获取城市天气 + 针对性生活建议，支持自然语言查询"""

    name: str = "get_weather"
    description: str = (
        "获取指定城市的当前天气信息，包括温度、湿度、天气状况、风速，以及穿衣和出行建议。"
        "输入可以为自然语言，如'北京今天热不热'、'上海会下雨吗'等。"
    )

    # Top-10 城市坐标（中英文），作为快速回退
    city_coords: ClassVar[Dict[str, Tuple[float, float]]] = {
        "北京": (39.9042, 116.4074),
        "上海": (31.2304, 121.4737),
        "广州": (23.1291, 113.2644),
        "深圳": (22.5431, 114.0579),
        "杭州": (30.2741, 120.1551),
        "成都": (30.5728, 104.0668),
        "重庆": (29.4316, 106.9123),
        "武汉": (30.5928, 114.3055),
        "南京": (32.0603, 118.7969),
        "西安": (34.3416, 108.9398),
        "Beijing": (39.9042, 116.4074),
        "Shanghai": (31.2304, 121.4737),
        "Guangzhou": (23.1291, 113.2644),
        "Shenzhen": (22.5431, 114.0579),
        "Hangzhou": (30.2741, 120.1551),
        "Chengdu": (30.5728, 104.0668),
        "Chongqing": (29.4316, 106.9123),
        "Wuhan": (30.5928, 114.3055),
        "Nanjing": (32.0603, 118.7969),
        "Xian": (34.3416, 108.9398),
    }

    # ------------------------------------------------------------------
    def _extract_city(self, query: str) -> str | None:
        """使用 LLM 从自然语言查询中提取城市名称"""
        # 快速路径：直接匹配内置城市名
        for city in self.city_coords:
            if city in query:
                return city

        # LLM 回退
        prompt = (
            "请从以下用户查询中提取城市名称。只返回城市中文名，不要返回其他内容。\n"
            '如果无法识别城市，返回"无"。\n\n'
            f"用户查询：{query}"
        )
        try:
            llm = _get_llm()
            response = llm.invoke([{"role": "user", "content": prompt}])
            city = response.content.strip().strip("'\"。， ")
            if city and city != "无":
                return city
        except Exception as e:
            logger.warning("LLM city extraction failed: %s", e)
        return None

    # ------------------------------------------------------------------
    def _geocode(self, city: str) -> Tuple[float, float] | None:
        """地理编码：先用内置字典，再用 LLM 推断坐标"""
        # 1) 内置字典
        if city in self.city_coords:
            return self.city_coords[city]

        # 2) LLM 地理编码
        prompt = (
            f'请返回"{city}"的经纬度坐标，格式为JSON：{{"lat": 纬度, "lon": 经度}}。'
            f'只返回JSON，不要包含其他内容。'
        )
        try:
            llm = _get_llm()
            response = llm.invoke([{"role": "user", "content": prompt}])
            raw = response.content.strip()
            # 提取 JSON 部分
            m = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
            if m:
                coords = json.loads(m.group())
                lat = float(coords.get("lat", coords.get("latitude", 0)))
                lon = float(coords.get("lon", coords.get("lng", coords.get("longitude", 0))))
                return (lat, lon)
        except Exception as e:
            logger.warning("LLM geocoding failed for '%s': %s", city, e)
        return None

    # ------------------------------------------------------------------
    @staticmethod
    def _validate_coords(lat: float, lon: float) -> bool:
        return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0

    # ------------------------------------------------------------------
    @staticmethod
    def _fetch_weather(lat: float, lon: float) -> dict | None:
        """从 Open-Meteo 获取天气数据"""
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current_weather=true&hourly=temperature_2m,relative_humidity_2m,windspeed_10m&timezone=auto"
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    @staticmethod
    def _parse_focus(query: str) -> str:
        """从用户查询中提取关键关注点"""
        focus_keywords = {
            "温度|热|冷|冷不冷|热不热|多少度": "温度",
            "下雨|雨|伞|防雨|降水|阵雨|暴雨|雷": "是否下雨",
            "穿|衣服|衣物|外套|羽绒|夹克|短袖|长袖|秋裤|保暖": "穿衣建议",
            "风|风力|刮风|大风|台风": "风力",
            "湿度|潮湿|干燥": "湿度",
            "空气质量|AQI|口罩|污染|雾霾|PM": "空气质量",
            "出行|出去|户外|运动|旅游|游玩|散步|跑步": "出行建议",
        }
        user_focus = []
        for keywords, category in focus_keywords.items():
            if re.search(keywords, query):
                user_focus.append(category)
        return "、".join(user_focus) if user_focus else "综合建议"

    # ------------------------------------------------------------------
    def _run(self, query: str) -> str:
        """执行天气查询。query 支持自然语言，如'北京今天热不热'。"""
        try:
            # 1) 提取城市
            city = self._extract_city(query)
            if not city:
                return "抱歉，无法从您的查询中识别出城市名称。请告知具体城市，如'北京'、'上海'等。"

            # 2) 地理编码
            coords = self._geocode(city)
            if not coords:
                return f"无法获取{city}的地理坐标，请尝试其他城市。"

            lat, lon = coords
            if not self._validate_coords(lat, lon):
                return f"获取到的{city}坐标无效 (lat={lat}, lon={lon})，请重试。"

            # 3) 获取天气数据
            data = self._fetch_weather(lat, lon)
            current = data["current_weather"]
            temp_c = current["temperature"]
            wind_speed = current["windspeed"]
            weather_code = current["weathercode"]
            weather_desc = WEATHER_DESCRIPTIONS.get(weather_code, "未知")

            # 湿度
            hourly = data["hourly"]
            current_time = current["time"]
            time_index = hourly["time"].index(current_time) if current_time in hourly["time"] else 0
            humidity = hourly["relative_humidity_2m"][time_index]

            weather_info = (
                f"城市: {city}\n"
                f"天气: {weather_desc}\n"
                f"温度: {temp_c}°C\n"
                f"湿度: {humidity}%\n"
                f"风速: {wind_speed} km/h\n"
                f"空气质量: 良好"
            )

            # 4) 提取关注点 + 生成建议
            user_focus = self._parse_focus(query)
            prompt = WEATHER_PROMPT.format(weather_info=weather_info, user_focus=user_focus)
            llm = _get_llm()
            advice = llm.invoke([{"role": "user", "content": prompt}])
            return advice.content.strip()

        except requests.exceptions.Timeout:
            return "天气查询超时，请稍后重试。"
        except requests.exceptions.HTTPError as e:
            return f"天气API请求失败（HTTP {e.response.status_code if e.response else '?'}），请稍后重试。"
        except requests.exceptions.RequestException:
            return "无法连接天气服务，请检查网络后重试。"
        except Exception as e:
            logger.exception("WeatherTool._run failed")
            return f"天气查询失败: {str(e)}"

    # ------------------------------------------------------------------
    async def _arun(self, query: str) -> str:
        return self._run(query)
