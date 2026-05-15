"""
兼容别名 — 请直接导入 session_store

此文件为 session_memory.py 的向后兼容层。
所有实现已迁移至 session_store.py。
"""
from session_store import (
    get_or_create_session,
    add_message,
    get_history,
    clear_history,
    get_context_window,
    set_preference,
    get_preference,
    get_all_preferences,
    delete_preferences,
    Message,
    sessions,
    preferences,
)
