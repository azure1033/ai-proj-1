from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
from weather_agent import get_weather_advice, get_weather_advice_with_focus
from pypdf import PdfReader
import docx
from model_config import get_openai_client, IS_OLLAMA, MODEL
from session_memory import (
    get_or_create_session,
    add_message,
    get_history as get_session_history,
    clear_history as clear_session_history,
    get_context_window,
    set_preference,
    get_all_preferences,
    delete_preferences,
)
from session_manager import (
    list_sessions,
    get_session,
    create_session,
    update_session,
    delete_session,
)

HISTORY_FILE = Path(__file__).parent / "chat_history.json"
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
DOCUMENTS: list[dict] = []


def extract_text_from_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext == ".txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".pdf":
        reader = PdfReader(str(file_path))
        text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
        return "\n\n".join(text)
    if ext == ".docx":
        doc = docx.Document(str(file_path))
        text = [p.text for p in doc.paragraphs]
        return "\n\n".join(text)
    raise ValueError(f"不支持的文件类型：{ext}")


def save_uploaded_file(upload_file: UploadFile) -> tuple[Path, str]:
    filename = Path(upload_file.filename or 'uploaded_file').name
    dest = UPLOAD_DIR / f"{uuid4().hex}_{filename}"
    with dest.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    upload_file.file.close()
    return dest, filename


def append_document(filename: str, text: str) -> dict:
    doc_id = uuid4().hex
    document = {
        "id": doc_id,
        "filename": filename,
        "text": text,
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
    }
    DOCUMENTS.append(document)
    return document


def get_documents_context() -> str:
    if not DOCUMENTS:
        return ""
    context_pieces = []
    for doc in DOCUMENTS:
        snippet = doc["text"]
        if len(snippet) > 6000:
            snippet = snippet[:6000] + "\n..."
        context_pieces.append(f"文件名：{doc['filename']}\n内容：{snippet}")
    return "\n\n".join(context_pieces)


def handle_document_query(query: str) -> str:
    context = get_documents_context()
    prompt = (
        "你是一个智能助手。以下是用户上传的文档内容。请基于这些文档回答问题。"
        "如果文档中没有相关信息，请如实说明\n\n"
        f"文档内容：\n{context}\n\n用户问题：{query}\n"
        "请只基于文档内容作答，并在答案中说明引用自文档的部分。"
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
    )
    return (response.choices[0].message.content or "").strip()

app = FastAPI(title="AI 智能问答助手", description="基于大语言模型的多技能AI助手")

# 添加CORS中间件，允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置OpenAI客户端（根据环境变量自动选择 Ollama 或远程 API）
client = get_openai_client()

class WeatherRequest(BaseModel):
    city: str | None = None
    query: str | None = None

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
    session_id: str | None = None


def ensure_history_file() -> None:
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def load_history() -> list:
    ensure_history_file()
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_history(history: list) -> None:
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def append_history_entry(entry: dict) -> None:
    history = load_history()
    history.append(entry)
    save_history(history)


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
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10
    )
    intent = response.choices[0].message.content or ""
    return intent.strip()

def handle_qa(query: str) -> str:
    prompt = f"请回答以下问题：{query}"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return (response.choices[0].message.content or "").strip()

def handle_qa_with_context(query: str, history: list, preference_context: str = "") -> str:
    """带上下文的问答处理"""
    # 构建消息列表
    messages = []
    
    # 系统提示
    system_prompt = (
        "你是一个智能助手。请根据对话历史和用户偏好来回答当前问题。"
        "如果用户提到之前的内容，请结合上下文进行回答。"
        + preference_context
    )
    messages.append({"role": "system", "content": system_prompt})
    
    # 历史消息（用于上下文理解）
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # 当前问题
    messages.append({"role": "user", "content": query})
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=500
    )
    return (response.choices[0].message.content or "").strip()

def handle_summarize(query: str) -> str:
    prompt = f"请总结以下内容：{query}"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return (response.choices[0].message.content or "").strip()

def handle_translate(query: str) -> str:
    prompt = f"请将以下文本翻译成中文：{query}"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return (response.choices[0].message.content or "").strip()

def handle_code_explain(query: str) -> str:
    prompt = f"请解释以下代码：{query}"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return (response.choices[0].message.content or "").strip()


@app.post("/documents/upload")
def upload_document(file: UploadFile = File(...)):
    try:
        dest, filename = save_uploaded_file(file)
        text = extract_text_from_file(dest)
        document = append_document(filename, text)
        return {"id": document["id"], "filename": filename, "uploaded_at": document["uploaded_at"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@app.get("/documents")
def list_documents():
    return {"documents": [{"id": d["id"], "filename": d["filename"], "uploaded_at": d["uploaded_at"]} for d in DOCUMENTS]}


@app.delete("/documents")
def clear_documents():
    DOCUMENTS.clear()
    return {"status": "ok", "message": "文档已清空"}


@app.post("/ask")
def ask(request: QueryRequest):
    # 获取或创建会话
    session_id = get_or_create_session(request.session_id)
    
    # 添加用户消息到历史
    add_message(session_id, "user", request.query)
    
    # 获取上下文窗口（用于 LLM）
    context_window = get_context_window(session_id, request.query)
    
    # 获取用户偏好
    prefs = get_all_preferences(session_id)
    preference_context = ""
    if prefs:
        pref_lines = [f"- {k}: {v}" for k, v in prefs.items()]
        preference_context = f"\n\n用户偏好：\n" + "\n".join(pref_lines)
    
    if DOCUMENTS:
        result = handle_document_query(request.query)
        intent = "文档问答"
    else:
        intent = classify_intent(request.query)
        
        # 根据意图调用对应的处理函数
        if intent == "天气查询":
            result = get_weather_advice_with_focus(request.query)
        elif intent == "问答":
            result = handle_qa_with_context(request.query, context_window, preference_context)
        elif intent == "总结":
            result = handle_summarize(request.query)
        elif intent == "翻译":
            result = handle_translate(request.query)
        elif intent == "代码解释":
            result = handle_code_explain(request.query)
        else:
            result = handle_qa_with_context(request.query, context_window, preference_context)
    
    # 添加助手回复到历史
    add_message(session_id, "assistant", result)

    return {"intent": intent, "response": result, "session_id": session_id}


@app.get("/history")
def get_history_endpoint(session_id: str = Query(..., description="会话ID")):
    """获取指定会话的历史消息"""
    return {"session_id": session_id, "messages": get_session_history(session_id)}


@app.post("/history/clear")
def clear_history_endpoint(session_id: str = Query(..., description="会话ID")):
    """清除指定会话的历史"""
    clear_session_history(session_id)
    return {"status": "ok", "message": "会话历史已清空", "session_id": session_id}


class PreferencesRequest(BaseModel):
    session_id: str
    key: str
    value: str


@app.post("/preferences")
def save_preference(request: PreferencesRequest):
    """保存用户偏好"""
    set_preference(request.session_id, request.key, request.value)
    return {"status": "ok", "session_id": request.session_id, "key": request.key, "value": request.value}


@app.get("/preferences")
def get_preferences_endpoint(session_id: str = Query(..., description="会话ID")):
    """获取用户偏好"""
    return {"session_id": session_id, "preferences": get_all_preferences(session_id)}


@app.delete("/preferences")
def delete_preferences_endpoint(session_id: str = Query(..., description="会话ID")):
    """删除用户偏好"""
    delete_preferences(session_id)
    return {"status": "ok", "message": "偏好已删除", "session_id": session_id}


# ============ 会话管理 API ============

class CreateSessionRequest(BaseModel):
    name: str | None = None


class UpdateSessionRequest(BaseModel):
    name: str


@app.get("/sessions")
def get_sessions():
    """列出所有会话"""
    sessions_list = list_sessions()
    return {"sessions": sessions_list}


@app.post("/sessions")
def create_new_session(request: CreateSessionRequest | None = None):
    """创建新会话"""
    meta = create_session(name=request.name if request else None)
    return {"session": meta}


@app.get("/sessions/{session_id}")
def get_session_detail(session_id: str):
    """获取会话详情"""
    meta = get_session(session_id)
    if not meta:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session": meta}


@app.patch("/sessions/{session_id}")
def update_session_name(session_id: str, request: UpdateSessionRequest):
    """更新会话名称"""
    meta = update_session(session_id, request.name)
    if not meta:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session": meta}


@app.delete("/sessions/{session_id}")
def delete_session_endpoint(session_id: str):
    """删除会话"""
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"status": "ok", "message": "会话已删除", "session_id": session_id}


@app.get("/sessions/{session_id}/history")
def get_session_messages(session_id: str):
    """获取会话消息历史"""
    history = get_session_history(session_id)
    return {"session_id": session_id, "messages": history}


@app.delete("/history")
def clear_history():
    save_history([])
    return {"status": "ok", "message": "聊天历史已清空"}


@app.get("/")
def root():
    return {"message": "AI 智能问答助手 API"}