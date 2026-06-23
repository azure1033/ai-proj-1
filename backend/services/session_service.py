"""
Session service — thin delegation layer over session_store.py.
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from session_store import (
    list_sessions,
    create_session,
    get_session,
    update_session,
    delete_session,
)
from tools.rag_tool import delete_session_collection

logger = logging.getLogger(__name__)


async def list_all_sessions(db: AsyncSession | None) -> list:
    """List all sessions."""
    return await list_sessions(db=db)


async def create_new_session(name: str | None, db: AsyncSession | None):
    """Create a new session."""
    return await create_session(name=name, db=db)


async def get_session_detail(session_id: str, db: AsyncSession | None):
    """Get session details by ID."""
    return await get_session(session_id, db=db)


async def update_session_name(session_id: str, name: str, db: AsyncSession | None):
    """Update session name."""
    return await update_session(session_id, name, db=db)


async def delete_session_and_cleanup(session_id: str, db: AsyncSession | None) -> bool:
    """Delete a session and its RAG data."""
    success = await delete_session(session_id, db=db)
    if not success:
        return False
    try:
        delete_session_collection(session_id)
    except Exception as e:
        logger.warning(f"清理会话 RAG 数据失败: {e}")
    return True
