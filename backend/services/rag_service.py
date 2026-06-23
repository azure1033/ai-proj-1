"""
RAG service — RAG status, settings management extracted from main.py.
"""
import logging

from tools.rag_tool import (
    get_vector_store,
    save_rag_settings as _save_rag_settings,
    load_rag_settings as _load_rag_settings,
)
from services.document_service import _document_registry

logger = logging.getLogger(__name__)


def get_rag_status(session_id: str) -> dict:
    """Get RAG status for a session (document count, chunk count, model status)."""
    try:
        vs = get_vector_store(session_id)
        count = vs._collection.count() if vs._collection else 0
        session_docs = _document_registry.get(session_id, [])
        return {
            "session_id": session_id,
            "document_count": len([d for d in session_docs if d.get("indexed")]),
            "total_chunks": count,
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


def save_rag_settings(settings: dict) -> dict:
    """Save RAG settings to disk."""
    _save_rag_settings(settings)
    return {"status": "ok", "settings": settings}


def load_rag_settings() -> dict:
    """Load RAG settings from disk."""
    return _load_rag_settings()
