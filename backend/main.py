"""
AI 智能问答助手 — FastAPI app factory.

All route handlers are in routers/. This file only handles:
- App creation & middleware
- Global exception handlers
- Startup/shutdown events
- Router registration
"""

import logging
import asyncio
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.logging import setup_logging
from database import get_db, init_db, is_mysql_enabled
from provider_manager import get_provider_manager

logger = logging.getLogger(__name__)

# ── App ─────────────────────────────────────────────────────

app = FastAPI(title="AI 智能问答助手", description="基于大语言模型的多技能AI助手")

# ── Exception Handlers ──────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Request Error", "detail": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"error": "Validation Error", "detail": errors})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": "服务器内部错误，请稍后重试"},
    )


# ── Middleware ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5175",
        "http://localhost",
        "http://frontend",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Observability Middleware ──────────────────────────────────

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed_ms = int((time.time() - start) * 1000)

    if request.url.path == "/ask" and request.method == "POST" and response.status_code < 500:
        asyncio.create_task(_log_request(request, response, elapsed_ms))

    return response


async def _log_request(request: Request, response, elapsed_ms: int):
    try:
        from database import get_db
        from services.observability_service import save_request_log

        async for db in get_db():
            if db is None:
                break
            # Extract body (already consumed by FastAPI, try reading from state)
            body = getattr(request.state, "_body", None)
            session_id = "unknown"
            error = None
            tokens_in = tokens_out = tool_calls = 0
            provider_id = model_name = None

            if response.status_code >= 400:
                error = f"HTTP {response.status_code}"

            await save_request_log(
                db, session_id=session_id, provider_id=provider_id, model_name=model_name,
                tokens_in=tokens_in, tokens_out=tokens_out, latency_ms=elapsed_ms,
                tool_calls=tool_calls, error=error,
            )
            await db.commit()
            break
    except Exception:
        pass  # Logging should never break the app

# ── Routers ─────────────────────────────────────────────────

from routers.chat import router as chat_router
from routers.documents import router as documents_router
from routers.sessions import router as sessions_router
from routers.providers import router as providers_router
from routers.rag import router as rag_router
from routers.weather import router as weather_router
from routers.preferences import router as preferences_router
from routers.metrics import router as metrics_router

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(sessions_router)
app.include_router(providers_router)
app.include_router(rag_router)
app.include_router(weather_router)
app.include_router(preferences_router)
app.include_router(metrics_router)


# ── Startup ─────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    setup_logging()

    if is_mysql_enabled():
        logger.info("MySQL 模式已启用，初始化数据库...")
        await init_db()

        # 旧数据迁移
        from services.chat_service import migrate_chat_history_json

        async for db in get_db():
            if db is not None:
                try:
                    await migrate_chat_history_json(db)
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    logger.warning(f"数据迁移失败（不影响正常使用）: {e}")
            break

        # 加载 provider 配置
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


# ── Root ────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "AI 智能问答助手 API"}
