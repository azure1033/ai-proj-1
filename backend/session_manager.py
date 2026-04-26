"""
会话管理器 - 管理会话元数据

提供:
- 会话列表管理
- 会话创建、查询、更新、删除
- 与 session_memory.py 配合使用
"""

from datetime import datetime
from typing import TypedDict
from uuid import uuid4

from session_memory import sessions, get_history


class SessionMeta(TypedDict):
    """会话元数据结构"""
    id: str
    name: str
    created_at: str
    updated_at: str
    message_count: int
    preview: str


# 全局会话元数据存储: Dict[session_id, SessionMeta]
session_metadata: dict[str, SessionMeta] = {}


def create_session(session_id: str | None = None, name: str | None = None) -> SessionMeta:
    """
    创建新会话
    
    Args:
        session_id: 可选的会话 ID，不提供则自动生成
        name: 会话名称，默认 "新会话"
    
    Returns:
        会话元数据
    """
    sid = session_id or str(uuid4())
    
    # 从第一条用户消息提取预览
    history = get_history(sid)
    preview = ""
    for msg in history:
        if msg["role"] == "user":
            preview = msg["content"][:30] + ("..." if len(msg["content"]) > 30 else "")
            break
    
    meta = SessionMeta(
        id=sid,
        name=name or "新会话",
        created_at=datetime.utcnow().isoformat() + "Z",
        updated_at=datetime.utcnow().isoformat() + "Z",
        message_count=len(history),
        preview=preview,
    )
    
    session_metadata[sid] = meta
    return meta


def get_session(session_id: str) -> SessionMeta | None:
    """获取会话元数据"""
    if session_id not in session_metadata:
        return None
    
    # 更新动态字段
    meta = session_metadata[session_id]
    history = get_history(session_id)
    meta["message_count"] = len(history)
    
    # 更新预览
    for msg in history:
        if msg["role"] == "user":
            content = msg["content"]
            meta["preview"] = content[:30] + ("..." if len(content) > 30 else "")
            break
    
    return meta


def list_sessions() -> list[SessionMeta]:
    """列出所有会话，按更新时间降序"""
    result = []
    for sid in session_metadata:
        meta = get_session(sid)
        if meta:
            result.append(meta)
    
    # 按 updated_at 降序排列
    result.sort(key=lambda x: x["updated_at"], reverse=True)
    return result


def update_session(session_id: str, name: str) -> SessionMeta | None:
    """更新会话（重命名）"""
    if session_id not in session_metadata:
        return None
    
    session_metadata[session_id]["name"] = name
    session_metadata[session_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return session_metadata[session_id]


def delete_session(session_id: str) -> bool:
    """删除会话"""
    if session_id not in session_metadata:
        return False
    
    # 删除元数据
    del session_metadata[session_id]
    
    # 删除消息历史（如果存在）
    if session_id in sessions:
        del sessions[session_id]
    
    return True


def touch_session(session_id: str) -> None:
    """更新会话的更新时间"""
    if session_id in session_metadata:
        session_metadata[session_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"


def get_or_create_session_meta(session_id: str | None = None) -> tuple[str, SessionMeta]:
    """
    获取或创建会话元数据
    
    Returns:
        (session_id, session_meta)
    """
    if session_id and session_id in session_metadata:
        return session_id, session_metadata[session_id]
    
    sid = session_id or str(uuid4())
    meta = create_session(sid)
    return sid, meta