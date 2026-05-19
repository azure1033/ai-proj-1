from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import openai
import os
import json
import shutil
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
from weather_agent import get_weather_advice, get_weather_advice_with_focus
from pypdf import PdfReader
import docx
from model_config import IS_OLLAMA, MODEL
from provider_manager import get_provider_manager
from encryption import decrypt as _decrypt_key
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, init_db, is_mysql_enabled
from session_store import (
    get_or_create_session,
    add_message,
    get_history as get_session_history,
    clear_history as clear_session_history,
    set_preference,
    get_all_preferences,
    delete_preferences,
    list_sessions,
    get_session,
    create_session,
    update_session,
    delete_session,
)
from agent import run_agent, run_agent_stream
from tools.rag_tool import set_rag_session

logger = logging.getLogger(__name__)

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
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
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
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
    )
    return (response.choices[0].message.content or "").strip()


app = FastAPI(title="AI 智能问答助手", description="基于大语言模型的多技能AI助手")

# 添加CORS中间件，允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:5175",   # Vite dev server (alt port)
        "http://localhost",        # Docker nginx on host
        "http://frontend",         # Docker internal service name
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置OpenAI客户端（动态加载，切换 provider 无需重启）
def _get_client():
    return get_provider_manager().get_active_llm_client()


# ============================================================
# 启动事件: 数据库初始化 + 旧数据迁移
# ============================================================

HISTORY_FILE = Path(__file__).parent / "chat_history.json"


async def _migrate_chat_history_json(db: AsyncSession) -> None:
    """将 chat_history.json 迁移到 MySQL"""
    import json as _json

    if not HISTORY_FILE.exists():
        return

    logger.info("检测到 chat_history.json，开始迁移到 MySQL...")
    try:
        raw = _json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (_json.JSONDecodeError, Exception) as e:
        logger.warning(f"读取 chat_history.json 失败: {e}，跳过迁移")
        return

    if not raw or not isinstance(raw, list):
        logger.info("chat_history.json 为空，跳过迁移")
        return

    # 创建 "历史记录" 会话
    from models import SessionModel
    legacy_id = "legacy-" + uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    db.add(SessionModel(
        id=legacy_id,
        name="历史记录",
        created_at=now,
        updated_at=now,
    ))
    await db.flush()

    # 逐条导入消息
    from models import MessageModel, MessageRole
    count = 0
    for entry in raw:
        role_str = entry.get("role", "user")
        content = entry.get("content", "")
        intent = entry.get("intent")

        if not content:
            continue

        db.add(MessageModel(
            session_id=legacy_id,
            role=MessageRole.user if role_str == "user" else MessageRole.assistant,
            content=str(content),
            intent=str(intent) if intent else None,
            created_at=datetime.now(timezone.utc),
        ))
        count += 1

    await db.flush()
    logger.info(f"迁移完成: {count} 条消息 -> 会话 '{legacy_id}'")

    # 重命名原文件防止重复迁移
    migrated_path = HISTORY_FILE.with_suffix(".json.migrated")
    HISTORY_FILE.rename(migrated_path)
    logger.info(f"chat_history.json 已重命名为 {migrated_path.name}")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    if is_mysql_enabled():
        logger.info("MySQL 模式已启用，初始化数据库...")
        await init_db()

        # 执行旧数据迁移
        async for db in get_db():
            if db is not None:
                try:
                    await _migrate_chat_history_json(db)
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    logger.warning(f"数据迁移失败（不影响正常使用）: {e}")
            break

        # 加载模型提供商配置
        async for db in get_db():
            if db is not None:
                try:
                    await get_provider_manager().reload_from_db(db)
                    await db.commit()
                except Exception as e:
                    logger.warning(f"加载 provider 配置失败: {e}")
            break
    else:
        logger.info("USE_MYSQL=false，使用内存 dict 模式（开发环境）")


class WeatherRequest(BaseModel):
    city: str | None = None
    query: str | None = None


@app.post("/weather")
def get_weather(request: WeatherRequest):
    try:
        if request.query:
            result = get_weather_advice_with_focus(request.query)
        elif request.city:
            result = get_weather_advice(request.city)
        else:
            raise ValueError("请提供城市名称（city）或自然语言查询（query）")
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"天气查询失败: {str(e)}")


class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None


def handle_qa(query: str) -> str:
    prompt = f"请回答以下问题：{query}"
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return (response.choices[0].message.content or "").strip()


def handle_qa_with_context(query: str, history: list, preference_context: str = "") -> str:
    """带上下文的问答处理"""
    messages = []

    system_prompt = (
        "你是一个智能助手。请根据对话历史和用户偏好来回答当前问题。"
        "如果用户提到之前的内容，请结合上下文进行回答。"
        + preference_context
    )
    messages.append({"role": "system", "content": system_prompt})

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": query})

    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=500
    )
    return (response.choices[0].message.content or "").strip()


def handle_summarize(query: str) -> str:
    prompt = f"请总结以下内容：{query}"
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return (response.choices[0].message.content or "").strip()


def handle_translate(query: str) -> str:
    prompt = f"请将以下文本翻译成中文：{query}"
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return (response.choices[0].message.content or "").strip()


def handle_code_explain(query: str) -> str:
    prompt = f"请解释以下代码：{query}"
    response = _get_client().chat.completions.create(
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
        try:
            from tools.rag_tool import ingest_document
            set_rag_session("default")
            session_id = "default"
            chunk_count = ingest_document(text, {"doc_id": document["id"], "filename": filename}, session_id)
            document["chunks"] = chunk_count if chunk_count >= 0 else 0
            document["indexed"] = chunk_count >= 0
        except Exception:
            document["chunks"] = 0
            document["indexed"] = False
        return {"id": document["id"], "filename": filename, "uploaded_at": document["uploaded_at"], "chunks": document.get("chunks", 0), "indexed": document.get("indexed", False)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@app.get("/documents")
def list_documents():
    return {"documents": [{"id": d["id"], "filename": d["filename"], "uploaded_at": d["uploaded_at"], "chunks": d.get("chunks", 0), "indexed": d.get("indexed", False)} for d in DOCUMENTS]}


@app.delete("/documents")
def clear_documents():
    DOCUMENTS.clear()
    return {"status": "ok", "message": "文档已清空"}


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    global DOCUMENTS
    doc = next((d for d in DOCUMENTS if d["id"] == doc_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    try:
        from tools.rag_tool import delete_document_vectors
        delete_document_vectors(doc_id, "default")
    except Exception as e:
        logger.warning(f"删除文档向量失败: {e}")
    for f in UPLOAD_DIR.iterdir():
        if doc_id in f.name:
            f.unlink(missing_ok=True)
    DOCUMENTS = [d for d in DOCUMENTS if d["id"] != doc_id]
    return {"status": "ok", "message": "文档已删除", "doc_id": doc_id}


@app.post("/ask")
async def ask(request: QueryRequest, stream: bool = Query(False), db: AsyncSession = Depends(get_db)):
    """统一对话接口，支持流式和非流式"""
    session_id = await get_or_create_session(request.session_id, db=db)
    await add_message(session_id, "user", request.query, db=db)
    set_rag_session(session_id)

    if stream:
        async def generate_sse():
            full_response = ""
            try:
                async for event in run_agent_stream(request.query):
                    event_type = event["type"]
                    event_data = event["data"]
                    if event_type == "token":
                        full_response += event_data
                    elif event_type == "done":
                        pass
                    yield f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                await add_message(session_id, "assistant", full_response, "Agent", db=db)
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        agent_result = run_agent(request.query)
        await add_message(session_id, "assistant", agent_result["response"], "Agent", db=db)
        return {
            "intent": "Agent",
            "response": agent_result["response"],
            "session_id": session_id,
            "steps": agent_result["steps"],
        }


@app.get("/history")
async def get_history_endpoint(session_id: str = Query(..., description="会话ID"), db: AsyncSession = Depends(get_db)):
    """获取指定会话的历史消息"""
    return {"session_id": session_id, "messages": await get_session_history(session_id, db=db)}


@app.post("/history/clear")
async def clear_history_endpoint(session_id: str = Query(..., description="会话ID"), db: AsyncSession = Depends(get_db)):
    """清除指定会话的历史"""
    await clear_session_history(session_id, db=db)
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
async def get_sessions(db: AsyncSession = Depends(get_db)):
    """列出所有会话"""
    sessions_list = await list_sessions(db=db)
    return {"sessions": sessions_list}


@app.post("/sessions")
async def create_new_session(request: CreateSessionRequest | None = None, db: AsyncSession = Depends(get_db)):
    """创建新会话"""
    meta = await create_session(name=request.name if request else None, db=db)
    return {"session": meta}


@app.get("/sessions/{session_id}")
async def get_session_detail(session_id: str, db: AsyncSession = Depends(get_db)):
    """获取会话详情"""
    meta = await get_session(session_id, db=db)
    if not meta:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session": meta}


@app.patch("/sessions/{session_id}")
async def update_session_name(session_id: str, request: UpdateSessionRequest, db: AsyncSession = Depends(get_db)):
    """更新会话名称"""
    meta = await update_session(session_id, request.name, db=db)
    if not meta:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session": meta}


@app.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str, db: AsyncSession = Depends(get_db)):
    """删除会话"""
    success = await delete_session(session_id, db=db)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    try:
        from tools.rag_tool import delete_session_collection
        delete_session_collection(session_id)
    except Exception as e:
        logger.warning(f"清理会话 RAG 数据失败: {e}")
    return {"status": "ok", "message": "会话已删除", "session_id": session_id}


@app.get("/sessions/{session_id}/history")
async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """获取会话消息历史"""
    history = await get_session_history(session_id, db=db)
    return {"session_id": session_id, "messages": history}


class RagSettingsRequest(BaseModel):
    embedding_model: str = "text2vec-base-chinese"
    device: str = "cpu"
    chunk_size: int = 384
    chunk_overlap: int = 64
    retrieval_k: int = 4
    load_strategy: str = "lazy"


@app.get("/rag/status")
def get_rag_status(session_id: str = Query(..., description="会话ID")):
    from tools.rag_tool import get_vector_store
    try:
        vs = get_vector_store(session_id)
        count = vs._collection.count() if vs._collection else 0
        total_chunks = count
        return {
            "session_id": session_id,
            "document_count": len([d for d in DOCUMENTS if d.get("indexed")]),
            "total_chunks": total_chunks,
            "model_loaded": True,
        }
    except Exception as e:
        return {
            "session_id": session_id,
            "document_count": 0,
            "total_chunks": 0,
            "model_loaded": False,
            "error": str(e),
        }


@app.post("/rag/settings")
def save_rag_settings(request: RagSettingsRequest):
    from tools.rag_tool import save_rag_settings as _save_rag_settings
    settings = request.model_dump()
    _save_rag_settings(settings)
    return {"status": "ok", "settings": settings}


@app.get("/rag/settings")
def get_rag_settings():
    from tools.rag_tool import load_rag_settings
    return load_rag_settings()


# ============ Provider 管理 API ============

class ProviderCreateRequest(BaseModel):
    id: str
    name: str
    provider_type: str  # "llm" | "embedding"
    base_url: str
    api_key: str = ""
    model_name: str


class ProviderUpdateRequest(BaseModel):
    name: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model_name: str | None = None


class ProviderTestRequest(BaseModel):
    api_key: str | None = None


class ProviderTestCustomRequest(BaseModel):
    base_url: str
    model_name: str
    api_key: str = ""


@app.get("/providers")
async def list_providers(db: AsyncSession = Depends(get_db)):
    """列出所有 provider（api_key 脱敏）"""
    from models import ModelProvider
    from sqlalchemy import select
    from encryption import mask_key

    result = await db.execute(select(ModelProvider).order_by(ModelProvider.provider_type, ModelProvider.id))
    providers = result.scalars().all()

    llm_list = []
    emb_list = []
    for p in providers:
        item = {
            "id": p.id,
            "name": p.name,
            "provider_type": p.provider_type.value,
            "base_url": p.base_url,
            "api_key": mask_key(_decrypt_key(p.api_key)) if p.api_key else "",
            "model_name": p.model_name,
            "is_active": p.is_active,
            "is_preset": p.is_preset,
            "is_local": p.is_local,
        }
        if p.provider_type.value == "llm":
            llm_list.append(item)
        else:
            emb_list.append(item)

    return {"llm": llm_list, "embedding": emb_list}


@app.post("/providers")
async def create_provider(request: ProviderCreateRequest, db: AsyncSession = Depends(get_db)):
    """新增自定义 provider"""
    from models import ModelProvider, ProviderType
    from sqlalchemy import select
    from encryption import encrypt

    # 检查 ID 是否已存在
    existing = await db.get(ModelProvider, request.id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Provider ID '{request.id}' 已存在")

    provider_type = ProviderType.llm if request.provider_type == "llm" else ProviderType.embedding
    encrypted_key = encrypt(request.api_key) if request.api_key else ""

    provider = ModelProvider(
        id=request.id,
        name=request.name,
        provider_type=provider_type,
        base_url=request.base_url,
        api_key=encrypted_key,
        model_name=request.model_name,
        is_active=False,
        is_preset=False,
        is_local=False,
    )
    db.add(provider)
    await db.flush()
    return {"id": provider.id, "name": provider.name, "message": "创建成功"}


@app.put("/providers/{provider_id}")
async def update_provider(provider_id: str, request: ProviderUpdateRequest, db: AsyncSession = Depends(get_db)):
    """更新 provider 配置（preset 仅允许更新 api_key）"""
    from models import ModelProvider
    from encryption import encrypt

    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider 不存在")

    if provider.is_preset:
        # preset 只能更新 api_key
        if request.api_key is not None:
            provider.api_key = encrypt(request.api_key)
        if request.name is not None or request.base_url is not None or request.model_name is not None:
            raise HTTPException(status_code=400, detail="预设 provider 只能修改 API Key")
    else:
        if request.name is not None:
            provider.name = request.name
        if request.base_url is not None:
            provider.base_url = request.base_url
        if request.api_key is not None:
            provider.api_key = encrypt(request.api_key)
        if request.model_name is not None:
            provider.model_name = request.model_name

    await db.flush()
    await get_provider_manager().reload_from_db(db)
    return {"id": provider.id, "message": "更新成功"}


@app.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str, db: AsyncSession = Depends(get_db)):
    """删除自定义 provider（preset 拒绝删除）"""
    from models import ModelProvider

    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider 不存在")
    if provider.is_preset:
        raise HTTPException(status_code=400, detail="预设 provider 不可删除")

    await db.delete(provider)
    await db.flush()
    return {"id": provider_id, "message": "已删除"}


@app.post("/providers/{provider_id}/activate")
async def activate_provider(provider_id: str, db: AsyncSession = Depends(get_db)):
    """激活指定 provider"""
    from models import ModelProvider
    from encryption import decrypt

    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider 不存在")

    # 非本地 provider 需要有效的 API Key
    if not provider.is_local:
        api_key = decrypt(provider.api_key) or ""
        if not api_key.strip():
            raise HTTPException(status_code=400, detail="请先设置 API Key 再激活该 Provider")

    success = await get_provider_manager().switch_provider(provider_id, db)
    if not success:
        raise HTTPException(status_code=500, detail="激活失败")
    return {"id": provider_id, "message": "已激活，即时生效"}


@app.post("/providers/{provider_id}/test")
async def test_provider(provider_id: str, request: ProviderTestRequest | None = None, db: AsyncSession = Depends(get_db)):
    """测试 provider 连接（可选使用请求中的 api_key）"""
    override_key = request.api_key if request and request.api_key else None
    result = await get_provider_manager().test_connection(provider_id, db, api_key_override=override_key)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "连接失败"))
    return result


@app.post("/providers/test-custom")
async def test_custom_provider(request: ProviderTestCustomRequest):
    """测试自定义 provider 连接（无需保存到 DB）"""
    import httpx

    api_key = request.api_key or ""
    base_url = request.base_url.rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            resp = await client.get(f"{base_url}/models", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                count = len(data.get("data", []))
                return {"success": True, "model_count": count, "message": f"连接成功，发现 {count} 个模型"}
            else:
                raise HTTPException(status_code=400, detail=f"HTTP {resp.status_code}: {resp.text[:200]}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=400, detail="连接超时（5s）")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def root():
    return {"message": "AI 智能问答助手 API"}
