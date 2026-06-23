"""Chat router — /ask, /history, /history/clear."""

import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.chat import QueryRequest
from services.chat_service import handle_chat_query
from session_store import get_history as get_session_history, clear_history as clear_session_history

router = APIRouter(tags=["Chat"])


@router.post("/ask")
async def ask(request: QueryRequest, stream: bool = Query(False), db: AsyncSession = Depends(get_db)):
    """统一对话接口，支持流式和非流式"""
    result = await handle_chat_query(request.query, request.session_id, stream, db)

    if stream:
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
        )
    return result


@router.get("/history")
async def get_history(session_id: str = Query(..., description="会话ID"), db: AsyncSession = Depends(get_db)):
    return {"session_id": session_id, "messages": await get_session_history(session_id, db=db)}


@router.post("/history/clear")
async def clear_history(session_id: str = Query(..., description="会话ID"), db: AsyncSession = Depends(get_db)):
    await clear_session_history(session_id, db=db)
    return {"status": "ok", "message": "会话历史已清空", "session_id": session_id}
