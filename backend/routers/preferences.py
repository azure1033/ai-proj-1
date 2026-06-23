"""Preferences router — /preferences."""

from fastapi import APIRouter, Query

from schemas.preferences import PreferencesRequest
from session_store import set_preference, get_all_preferences, delete_preferences

router = APIRouter(tags=["Preferences"])


@router.post("/preferences")
async def save_preference(request: PreferencesRequest):
    set_preference(request.session_id, request.key, request.value)
    return {"status": "ok", "session_id": request.session_id, "key": request.key, "value": request.value}


@router.get("/preferences")
async def get_preferences(session_id: str = Query(..., description="会话ID")):
    return {"session_id": session_id, "preferences": get_all_preferences(session_id)}


@router.delete("/preferences")
async def delete_preferences_endpoint(session_id: str = Query(..., description="会话ID")):
    delete_preferences(session_id)
    return {"status": "ok", "message": "偏好已删除", "session_id": session_id}
