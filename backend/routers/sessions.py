"""Sessions router — /sessions CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.sessions import CreateSessionRequest, UpdateSessionRequest
from services.session_service import (
    list_all_sessions,
    create_new_session,
    get_session_detail,
    update_session_name,
    delete_session_and_cleanup,
)
from session_store import get_history as get_session_history

router = APIRouter(tags=["Sessions"])


@router.get("/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    return {"sessions": await list_all_sessions(db=db)}


@router.post("/sessions")
async def create_session(request: CreateSessionRequest | None = None, db: AsyncSession = Depends(get_db)):
    meta = await create_new_session(name=request.name if request else None, db=db)
    return {"session": meta}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    meta = await get_session_detail(session_id, db=db)
    if not meta:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session": meta}


@router.patch("/sessions/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest, db: AsyncSession = Depends(get_db)):
    meta = await update_session_name(session_id, request.name, db=db)
    if not meta:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session": meta}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    success = await delete_session_and_cleanup(session_id, db=db)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"status": "ok", "message": "会话已删除", "session_id": session_id}


@router.get("/sessions/{session_id}/history")
async def session_history(session_id: str, db: AsyncSession = Depends(get_db)):
    history = await get_session_history(session_id, db=db)
    return {"session_id": session_id, "messages": history}
