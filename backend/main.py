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
    # 简单的意图分类，使用LLM
    prompt = f"请根据以下用户查询，判断意图属于以下哪一类：问答、总结、翻译、代码解释。只回复类别名称。\n查询：{query}"
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V2.5",  # 更新模型名
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
    if intent == "问答":
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