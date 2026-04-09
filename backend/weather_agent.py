import os
from typing import ClassVar, Dict, Tuple

import requests
from dotenv import load_dotenv
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V2.5",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.siliconflow.cn/",
    temperature=0.7,
)


class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "获取指定城市的当前天气信息。输入应为城市名称，如'北京'或'Beijing'。"

    city_coords: ClassVar[Dict[str, Tuple[float, float]]] = {
        "北京": (39.9042, 116.4074),
        "上海": (31.2304, 121.4737),
        "广州": (23.1291, 113.2644),
        "深圳": (22.5431, 114.0579),
        "合肥": (31.8206, 117.2272),
        "南京": (32.0603, 118.7969),
        "杭州": (30.2741, 120.1551),
        "武汉": (30.5928, 114.3055),
        "成都": (30.5728, 104.0668),
        "重庆": (29.4316, 106.9123),
        "西安": (34.3416, 108.9398),
        "天津": (39.3434, 117.3616),
        "苏州": (31.2989, 120.5853),
        "郑州": (34.7466, 113.6254),
        "长沙": (28.2282, 112.9388),
        "青岛": (36.0671, 120.3826),
        "沈阳": (41.8057, 123.4315),
        "大连": (38.9140, 121.6147),
        "厦门": (24.4798, 118.0894),
        "福州": (26.0745, 119.2965),
        "济南": (36.6512, 117.1201),
        "宁波": (29.8683, 121.5440),
        "无锡": (31.4912, 120.3119),
        "昆明": (25.0389, 102.7183),
        "哈尔滨": (45.8038, 126.5340),
        "长春": (43.8171, 125.3235),
        "南昌": (28.6820, 115.8579),
        "贵阳": (26.6470, 106.6302),
        "兰州": (36.0611, 103.8343),
        "太原": (37.8706, 112.5489),
        "乌鲁木齐": (43.8256, 87.6168),
        "呼和浩特": (40.8424, 111.7492),
        "银川": (38.4872, 106.2309),
        "西宁": (36.6234, 101.7782),
        "拉萨": (29.6500, 91.1000),
        "海口": (20.0440, 110.1999),
        "三亚": (18.2528, 109.5121),
        "南宁": (22.8170, 108.3669),
        "桂林": (25.2342, 110.2899),
        "柳州": (24.3652, 109.4281),
        "珠海": (22.2710, 113.5767),
        "中山": (22.5176, 113.3928),
        "惠州": (23.1108, 114.4160),
        "东莞": (23.0205, 113.7518),
        "佛山": (23.0215, 113.1214),
        "江门": (22.5787, 113.0815),
        "湛江": (21.2714, 110.3589),
        "茂名": (21.6633, 110.9255),
        "肇庆": (23.0472, 112.4650),
        "云浮": (22.9151, 112.0445),
        "阳江": (21.8583, 111.9826),
        "清远": (23.6820, 113.0561),
        "韶关": (24.8106, 113.5972),
        "河源": (23.7437, 114.7001),
        "梅州": (24.2884, 116.1226),
        "汕头": (23.3541, 116.6817),
        "揭阳": (23.5497, 116.3727),
        "汕尾": (22.7857, 115.3751),
        "潮州": (23.6567, 116.6226),
        "Shanghai": (31.2304, 121.4737),
        "Guangzhou": (23.1291, 113.2644),
        "Shenzhen": (22.5431, 114.0579),
        "Hefei": (31.8206, 117.2272),
        "Nanjing": (32.0603, 118.7969),
        "Hangzhou": (30.2741, 120.1551),
        "Wuhan": (30.5928, 114.3055),
        "Chengdu": (30.5728, 104.0668),
        "Chongqing": (29.4316, 106.9123),
        "Xian": (34.3416, 108.9398),
        "Tianjin": (39.3434, 117.3616),
        "Suzhou": (31.2989, 120.5853),
        "Zhengzhou": (34.7466, 113.6254),
        "Changsha": (28.2282, 112.9388),
        "Qingdao": (36.0671, 120.3826),
        "Shenyang": (41.8057, 123.4315),
        "Dalian": (38.9140, 121.6147),
        "Xiamen": (24.4798, 118.0894),
        "Fuzhou": (26.0745, 119.2965),
        "Jinan": (36.6512, 117.1201),
        "Ningbo": (29.8683, 121.5440),
        "Wuxi": (31.4912, 120.3119),
        "Kunming": (25.0389, 102.7183),
        "Harbin": (45.8038, 126.5340),
        "Changchun": (43.8171, 125.3235),
        "Nanchang": (28.6820, 115.8579),
        "Guiyang": (26.6470, 106.6302),
        "Lanzhou": (36.0611, 103.8343),
        "Taiyuan": (37.8706, 112.5489),
        "Urumqi": (43.8256, 87.6168),
        "Hohhot": (40.8424, 111.7492),
        "Yinchuan": (38.4872, 106.2309),
        "Xining": (36.6234, 101.7782),
        "Lhasa": (29.6500, 91.1000),
        "Haikou": (20.0440, 110.1999),
        "Sanya": (18.2528, 109.5121),
        "Nanning": (22.8170, 108.3669),
        "Guilin": (25.2342, 110.2899),
        "Liuzhou": (24.3652, 109.4281),
        "Zhuhai": (22.2710, 113.5767),
        "Zhongshan": (22.5176, 113.3928),
        "Huizhou": (23.1108, 114.4160),
        "Dongguan": (23.0205, 113.7518),
        "Foshan": (23.0215, 113.1214),
        "Jiangmen": (22.5787, 113.0815),
        "Zhanjiang": (21.2714, 110.3589),
        "Maoming": (21.6633, 110.9255),
        "Zhaoqing": (23.0472, 112.4650),
        "Yunfu": (22.9151, 112.0445),
        "Yangjiang": (21.8583, 111.9826),
        "Qingyuan": (23.6820, 113.0561),
        "Shaoguan": (24.8106, 113.5972),
        "Heyuan": (23.7437, 114.7001),
        "Meizhou": (24.2884, 116.1226),
        "Shantou": (23.3541, 116.6817),
        "Jieyang": (23.5497, 116.3727),
        "Shanwei": (22.7857, 115.3751),
        "Chaozhou": (23.6567, 116.6226),
    }

    def _run(self, city: str) -> str:
        try:
            if city not in self.city_coords:
                return f"不支持的城市: {city}。请尝试其他城市。"

            lat, lon = self.city_coords[city]
            url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                "&current_weather=true&hourly=temperature_2m,relative_humidity_2m,windspeed_10m&timezone=auto"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            current = data["current_weather"]
            temp_c = current["temperature"]
            wind_speed = current["windspeed"]
            weather_code = current["weathercode"]

            hourly = data["hourly"]
            current_time = current["time"]
            time_index = hourly["time"].index(current_time) if current_time in hourly["time"] else 0
            humidity = hourly["relative_humidity_2m"][time_index]

            weather_descriptions = {
                0: "晴朗",
                1: "大部分晴朗",
                2: "部分多云",
                3: "多云",
                45: "雾",
                48: "雾",
                51: "小雨",
                53: "中雨",
                55: "大雨",
                56: "小冻雨",
                57: "大冻雨",
                61: "小雨",
                63: "中雨",
                65: "大雨",
                66: "小冻雨",
                67: "大冻雨",
                71: "小雪",
                73: "中雪",
                75: "大雪",
                77: "雪粒",
                80: "小阵雨",
                81: "中阵雨",
                82: "大阵雨",
                85: "小阵雪",
                86: "大阵雪",
                95: "雷暴",
                96: "雷暴伴小冰雹",
                99: "雷暴伴大冰雹",
            }
            weather_desc = weather_descriptions.get(weather_code, "未知")
            air_quality = "良好"

            return (
                f"城市: {city}\n天气: {weather_desc}\n温度: {temp_c}°C\n湿度: {humidity}%\n风速: {wind_speed} km/h\n空气质量: {air_quality}"
            )
        except Exception as e:
            return f"获取天气信息失败: {str(e)}"

    def _arun(self, city: str):
        raise NotImplementedError("异步执行未实现")


weather_tool = WeatherTool()

weather_prompt = PromptTemplate.from_template(
    """
你是一个智能天气助手。基于以下天气信息，给出实用的生活建议。

天气信息: {weather_info}

请提供：
1. 当前天气状况总结
2. 相关的出行建议（如是否需要带伞、穿什么衣服等）
3. 健康建议（如空气质量相关的提醒）

用友好的语气回复。
"""
)


def get_weather_advice(city: str) -> str:
    weather_info = weather_tool._run(city)
    prompt = weather_prompt.format(weather_info=weather_info)
    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content
