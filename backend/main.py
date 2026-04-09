from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from weather_agent import get_weather_advice, get_weather_advice_with_focus

load_dotenv()

app = FastAPI(title="AI 智能问答助手", description="基于大语言模型的多技能AI助手")

# 添加CORS中间件，允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置OpenAI客户端，使用DeepSeek API (假设兼容OpenAI格式)
client = openai.OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.siliconflow.cn/"
)

class WeatherRequest(BaseModel):
    city: str = None
    query: str = None

@app.post("/weather")
def get_weather(request: WeatherRequest):
    try:
        # 支持自然语言查询（query参数）和传统查询（city参数）
        if request.query:
            # 使用自然语言处理
            result = get_weather_advice_with_focus(request.query)
        elif request.city:
            # 传统方式，直接查询城市
            result = get_weather_advice(request.city)
        else:
            raise ValueError("请提供城市名称（city）或自然语言查询（query）")
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"天气查询失败: {str(e)}")

class QueryRequest(BaseModel):
    query: str

def classify_intent(query: str) -> str:
    """
    智能意图分类，优先检查天气相关关键词，然后使用LLM进行分类。
    返回：天气查询、问答、总结、翻译、代码解释
    """
    # 天气相关关键词（中文）
    weather_keywords = [
        "天气", "天气如何", "天气怎么样",
        "温度", "多少度", "热", "冷", "热不热", "冷不冷",
        "下雨", "会下雨", "下雨吗", "下雪", "会下雪",
        "穿", "衣服", "衣物", "外套", "羽绒", "需要穿",
        "风", "风力", "刮风", "有没有风", "风大吗",
        "湿度", "潮湿", "干燥",
        "空气质量", "AQI", "口罩", "污染", "空气怎么样",
        "出行", "出去", "户外", "运动", "能不能出去",
        "紫外线", "阳光", "太阳",
        "雾霾", "雾", "能见度",
        "今天", "明天", "后天",
        "这里", "这个城市", "当地"
    ]
    
    query_lower = query.lower()
    
    # 检查是否包含天气关键词
    for keyword in weather_keywords:
        if keyword in query_lower or keyword in query:
            return "天气查询"
    
    # 如果没有匹配天气关键词，使用LLM进行分类
    prompt = f"请根据以下用户查询，判断意图属于以下哪一类：问答、总结、翻译、代码解释。只回复类别名称。\n查询：{query}"
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V2.5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10
    )
    intent = response.choices[0].message.content.strip()
    return intent

def handle_qa(query: str) -> str:
    prompt = f"请回答以下问题：{query}"
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V2.5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def handle_summarize(query: str) -> str:
    prompt = f"请总结以下内容：{query}"
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V2.5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def handle_translate(query: str) -> str:
    prompt = f"请将以下文本翻译成中文：{query}"
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V2.5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def handle_code_explain(query: str) -> str:
    prompt = f"请解释以下代码：{query}"
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V2.5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

@app.post("/ask")
def ask(request: QueryRequest):
    intent = classify_intent(request.query)
    
    # 根据意图调用对应的处理函数
    if intent == "天气查询":
        result = get_weather_advice_with_focus(request.query)
    elif intent == "问答":
        result = handle_qa(request.query)
    elif intent == "总结":
        result = handle_summarize(request.query)
    elif intent == "翻译":
        result = handle_translate(request.query)
    elif intent == "代码解释":
        result = handle_code_explain(request.query)
    else:
        result = handle_qa(request.query)  # 默认问答
    return {"intent": intent, "response": result}

@app.get("/")
def root():
    return {"message": "AI 智能问答助手 API"}