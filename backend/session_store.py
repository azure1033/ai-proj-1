"""
会话存储模块 — 统一的会话消息和元数据管理

合并自 session_memory.py + session_manager.py，消除循环导入。

支持双模式:
- MySQL 持久化模式 (USE_MYSQL=true): 通过 AsyncSession 读写数据库
- 内存 dict 模式 (默认): 保持向后兼容，开发环境无需 MySQL

提供:
- 会话级别消息存储、上下文窗口管理
- 会话元数据 CRUD
- 用户偏好存储（仅内存）
"""

from datetime import datetime, timezone
from typing import TypedDict, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update as sql_update, delete as sql_delete

# ============================================================
# 配置常量
# ============================================================

MAX_MESSAGES = 10  # 最近 10 轮对话
MAX_TOKENS = 4000  # 约 16000 字符


# ============================================================
# 类型定义
# ============================================================

class Message(TypedDict):
    role: str  # "user" or "assistant"
    content: str
    intent: str | None  # 意图标签，可选


class SessionMeta(TypedDict):
    """会话元数据结构"""
    id: str
    name: str
    created_at: str
    updated_at: str
    message_count: int
    preview: str


# ============================================================
# 内存回退存储（USE_MYSQL=false 时使用）
# ============================================================

# 会话消息: Dict[session_id, List[Message]]
sessions: dict[str, list[Message]] = {}

# 用户偏好: Dict[session_id, Dict[key, value]]
preferences: dict[str, dict[str, str]] = {}

# 会话元数据: Dict[session_id, SessionMeta]
session_metadata: dict[str, SessionMeta] = {}


# ============================================================
# 内部工具函数
# ============================================================

def _build_preview(messages: list) -> str:
    """从消息列表中提取第一条用户消息作为预览"""
    for msg in messages:
        if msg.get("role") == "user":
            content = msg["content"]
            return content[:30] + ("..." if len(content) > 30 else "")
    return ""


def _ensure_in_memory(session_id: str) -> None:
    """确保内存 dict 中存在该会话"""
    if session_id not in sessions:
        sessions[session_id] = []
    if session_id not in preferences:
        preferences[session_id] = {}


def _create_meta_in_memory(sid: str, name: str | None = None) -> SessionMeta:
    """在内存 dict 中创建会话元数据"""
    preview = _build_preview(sessions.get(sid, []))
    now = datetime.now(timezone.utc).isoformat()

    meta = SessionMeta(
        id=sid,
        name=name or "新会话",
        created_at=now,
        updated_at=now,
        message_count=len(sessions.get(sid, [])),
        preview=preview,
    )
    session_metadata[sid] = meta
    return meta


async def _refresh_meta_in_memory(session_id: str) -> SessionMeta | None:
    """刷新内存中的会话元数据动态字段"""
    if session_id not in session_metadata:
        return None
    meta = session_metadata[session_id]
    history = sessions.get(session_id, [])
    meta["message_count"] = len(history)
    meta["preview"] = _build_preview(history)
    return meta


async def _db_message_count(db: AsyncSession, session_id: str) -> int:
    """从 DB 查询会话消息数"""
    from models import MessageModel
    result = await db.execute(
        select(func.count(MessageModel.id)).where(MessageModel.session_id == session_id)
    )
    return result.scalar() or 0


async def _db_first_user_message(db: AsyncSession, session_id: str):
    """从 DB 查询会话第一条用户消息"""
    from models import MessageModel
    result = await db.execute(
        select(MessageModel)
        .where(MessageModel.session_id == session_id, MessageModel.role == "user")
        .order_by(MessageModel.created_at.asc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _db_session_to_meta(db: AsyncSession, session_id: str, model) -> SessionMeta:
    """将 DB SessionModel + 动态查询 → SessionMeta"""
    message_count = await _db_message_count(db, session_id)
    first_user = await _db_first_user_message(db, session_id)
    preview = _build_preview([{"role": "user", "content": first_user.content}] if first_user else [])

    return SessionMeta(
        id=model.id,
        name=model.name,
        created_at=model.created_at.isoformat() if model.created_at else "",
        updated_at=model.updated_at.isoformat() if model.updated_at else "",
        message_count=message_count,
        preview=preview,
    )


# ============================================================
# 公共 API — 消息管理
# ============================================================

async def get_or_create_session(
    session_id: str | None = None,
    db: AsyncSession | None = None,
) -> str:
    """获取或创建会话 ID"""
    if db is not None:
        if session_id:
            from models import SessionModel
            result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
            if result.scalar_one_or_none():
                return session_id
        new_id = session_id or str(uuid4())
        from models import SessionModel
        db.add(SessionModel(id=new_id))
        await db.flush()
        await create_session(new_id, db=db)
        return new_id

    # 内存 dict 模式
    if session_id and session_id in sessions:
        return session_id
    new_id = session_id or str(uuid4())
    sessions[new_id] = []
    preferences[new_id] = {}
    _create_meta_in_memory(new_id)
    return new_id


async def add_message(
    session_id: str,
    role: str,
    content: str,
    intent: str | None = None,
    db: AsyncSession | None = None,
) -> None:
    """添加消息到会话"""
    if db is not None:
        from models import MessageModel, MessageRole
        db.add(MessageModel(
            session_id=session_id,
            role=MessageRole.user if role == "user" else MessageRole.assistant,
            content=content,
            intent=intent,
        ))
        await db.flush()
        await touch_session(session_id, db=db)
        return

    _ensure_in_memory(session_id)
    msg: Message = {"role": role, "content": content}
    if intent:
        msg["intent"] = intent
    sessions[session_id].append(msg)
    await touch_session(session_id)


async def get_history(
    session_id: str,
    db: AsyncSession | None = None,
) -> list[Message]:
    """获取会话历史"""
    if db is not None:
        from models import MessageModel
        result = await db.execute(
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.asc())
        )
        models = result.scalars().all()
        messages: list[Message] = []
        for m in models:
            msg: Message = {"role": m.role.value, "content": m.content}
            if m.intent:
                msg["intent"] = m.intent
            messages.append(msg)
        return messages

    return sessions.get(session_id, [])


async def clear_history(
    session_id: str,
    db: AsyncSession | None = None,
) -> None:
    """清除会话历史"""
    if db is not None:
        from models import MessageModel
        await db.execute(sql_delete(MessageModel).where(MessageModel.session_id == session_id))
        await db.flush()
        return

    if session_id in sessions:
        sessions[session_id] = []


async def get_context_window(
    session_id: str,
    current_query: str = "",
    db: AsyncSession | None = None,
) -> list[Message]:
    """获取上下文窗口 — 限制消息数量和 token 数"""
    history = await get_history(session_id, db=db)
    if not history:
        return []

    windowed = history[-MAX_MESSAGES:] if len(history) > MAX_MESSAGES else history

    def estimate_tokens(messages: list[Message]) -> int:
        total = 0
        for msg in messages:
            total += len(msg["content"]) // 2 + 10
        return total

    while estimate_tokens(windowed) > MAX_TOKENS and len(windowed) > 1:
        windowed = windowed[1:]

    return windowed


# ============================================================
# 公共 API — 偏好管理（仅内存）
# ============================================================

def set_preference(session_id: str, key: str, value: str) -> None:
    _ensure_in_memory(session_id)
    preferences[session_id][key] = value


def get_preference(session_id: str, key: str) -> str | None:
    return preferences.get(session_id, {}).get(key)


def get_all_preferences(session_id: str) -> dict[str, str]:
    return preferences.get(session_id, {}).copy()


def delete_preferences(session_id: str) -> None:
    if session_id in preferences:
        del preferences[session_id]


# ============================================================
# 公共 API — 会话元数据管理
# ============================================================

async def create_session(
    session_id: str | None = None,
    name: str | None = None,
    db: AsyncSession | None = None,
) -> SessionMeta:
    """创建新会话"""
    sid = session_id or str(uuid4())

    if db is not None:
        from models import SessionModel
        result = await db.execute(select(SessionModel).where(SessionModel.id == sid))
        existing = result.scalar_one_or_none()
        if existing:
            return await _db_session_to_meta(db, sid, existing)

        now = datetime.now(timezone.utc)
        db.add(SessionModel(id=sid, name=name or "新会话", created_at=now, updated_at=now))
        await db.flush()
        await touch_session(sid, db=db)
        return SessionMeta(
            id=sid, name=name or "新会话",
            created_at=now.isoformat(), updated_at=now.isoformat(),
            message_count=0, preview="",
        )

    return _create_meta_in_memory(sid, name)


async def get_session(
    session_id: str,
    db: AsyncSession | None = None,
) -> SessionMeta | None:
    """获取会话元数据"""
    if db is not None:
        from models import SessionModel
        result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return await _db_session_to_meta(db, session_id, model)

    return await _refresh_meta_in_memory(session_id)


async def list_sessions(
    db: AsyncSession | None = None,
) -> list[SessionMeta]:
    """列出所有会话，按更新时间降序"""
    if db is not None:
        from models import SessionModel
        result = await db.execute(
            select(SessionModel).order_by(SessionModel.updated_at.desc())
        )
        models = result.scalars().all()
        metas = []
        for m in models:
            metas.append(await _db_session_to_meta(db, m.id, m))
        return metas

    result = []
    for sid in session_metadata:
        meta = await _refresh_meta_in_memory(sid)
        if meta:
            result.append(meta)
    result.sort(key=lambda x: x["updated_at"], reverse=True)
    return result


async def update_session(
    session_id: str,
    name: str,
    db: AsyncSession | None = None,
) -> SessionMeta | None:
    """更新会话（重命名）"""
    if db is not None:
        from models import SessionModel
        now = datetime.now(timezone.utc)
        await db.execute(
            sql_update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(name=name, updated_at=now)
        )
        await db.flush()
        return await get_session(session_id, db=db)

    if session_id not in session_metadata:
        return None
    session_metadata[session_id]["name"] = name
    session_metadata[session_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    return session_metadata[session_id]


async def delete_session(
    session_id: str,
    db: AsyncSession | None = None,
) -> bool:
    """删除会话（MySQL 模式下 CASCADE 自动删除消息）"""
    if db is not None:
        from models import SessionModel
        result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        model = result.scalar_one_or_none()
        if not model:
            return False
        await db.delete(model)
        await db.flush()
        return True

    if session_id not in session_metadata:
        return False
    del session_metadata[session_id]
    if session_id in sessions:
        del sessions[session_id]
    return True


async def touch_session(
    session_id: str,
    db: AsyncSession | None = None,
) -> None:
    """更新会话的更新时间"""
    if db is not None:
        from models import SessionModel
        now = datetime.now(timezone.utc)
        await db.execute(
            sql_update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(updated_at=now)
        )
        await db.flush()
        return

    if session_id in session_metadata:
        session_metadata[session_id]["updated_at"] = datetime.now(timezone.utc).isoformat()


async def get_or_create_session_meta(
    session_id: str | None = None,
    db: AsyncSession | None = None,
) -> tuple[str, SessionMeta]:
    """获取或创建会话元数据，返回 (session_id, session_meta)"""
    if db is not None:
        if session_id:
            meta = await get_session(session_id, db=db)
            if meta:
                return session_id, meta
        sid = session_id or str(uuid4())
        meta = await create_session(sid, db=db)
        return sid, meta

    if session_id and session_id in session_metadata:
        return session_id, session_metadata[session_id]

    sid = session_id or str(uuid4())
    meta = _create_meta_in_memory(sid)
    return sid, meta
