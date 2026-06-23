"""RAG router — /rag/status, /rag/settings."""

from fastapi import APIRouter, Query

from schemas.rag import RagSettingsRequest
from services.rag_service import get_rag_status, save_rag_settings, load_rag_settings

router = APIRouter(tags=["RAG"])


@router.get("/rag/status")
async def rag_status(session_id: str = Query(..., description="会话ID")):
    return get_rag_status(session_id)


@router.post("/rag/settings")
async def rag_save_settings(request: RagSettingsRequest):
    return save_rag_settings(request.model_dump())


@router.get("/rag/settings")
async def rag_get_settings():
    return load_rag_settings()
