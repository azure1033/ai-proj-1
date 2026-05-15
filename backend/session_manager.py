"""
兼容别名 — 请直接导入 session_store

此文件为 session_manager.py 的向后兼容层。
所有实现已迁移至 session_store.py。
"""
from session_store import (
    create_session,
    get_session,
    list_sessions,
    update_session,
    delete_session,
    touch_session,
    get_or_create_session_meta,
    SessionMeta,
    session_metadata,
)
