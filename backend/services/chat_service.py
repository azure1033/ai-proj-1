"""Chat service — handle the /ask endpoint logic, SSE streaming and non-streaming."""

import json
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from agent import run_agent, run_agent_stream
from session_store import get_or_create_session, add_message
from tools.rag_tool import set_rag_session

logger = logging.getLogger(__name__)


async def handle_chat_query(
    query: str,
    session_id: str | None,
    stream: bool,
    db: AsyncSession,
):
    """Handle a chat query — create/get session, add user message, execute agent.

    Returns:
        non-stream: dict {"intent", "response", "session_id", "steps"}
        stream: async generator yielding SSE strings
    """
    sid = await get_or_create_session(session_id, db=db)
    await add_message(sid, "user", query, db=db)
    set_rag_session(sid)

    if stream:
        return _generate_sse(query, sid, db)
    else:
        agent_result = run_agent(query)
        await add_message(sid, "assistant", agent_result["response"], "Agent", db=db)
        return {
            "intent": "Agent",
            "response": agent_result["response"],
            "session_id": sid,
            "steps": agent_result["steps"],
        }


async def _generate_sse(query: str, session_id: str, db: AsyncSession) -> AsyncGenerator[str, None]:
    """Generate SSE events from streaming agent execution."""
    full_response = ""
    try:
        async for event in run_agent_stream(query):
            event_type = event["type"]
            event_data = event["data"]
            if event_type == "token":
                full_response += event_data
            yield f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"
        await add_message(session_id, "assistant", full_response, "Agent", db=db)
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"


async def migrate_chat_history_json(db: AsyncSession) -> None:
    """将 chat_history.json 迁移到 MySQL（启动时调用一次）"""
    import json as _json
    from datetime import datetime, timezone
    from pathlib import Path
    from uuid import uuid4

    from models import SessionModel, MessageModel, MessageRole

    history_file = Path(__file__).parent.parent / "chat_history.json"
    if not history_file.exists():
        return

    logger.info("检测到 chat_history.json，开始迁移到 MySQL...")
    try:
        raw = _json.loads(history_file.read_text(encoding="utf-8"))
    except (_json.JSONDecodeError, Exception) as e:
        logger.warning(f"读取 chat_history.json 失败: {e}，跳过迁移")
        return

    if not raw or not isinstance(raw, list):
        logger.info("chat_history.json 为空，跳过迁移")
        return

    legacy_id = "legacy-" + uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    db.add(SessionModel(id=legacy_id, name="历史记录", created_at=now, updated_at=now))
    await db.flush()

    count = 0
    for entry in raw:
        role_str = entry.get("role", "user")
        content = entry.get("content", "")
        intent = entry.get("intent")
        if not content:
            continue
        db.add(MessageModel(
            session_id=legacy_id,
            role=MessageRole.user if role_str == "user" else MessageRole.assistant,
            content=str(content),
            intent=str(intent) if intent else None,
            created_at=datetime.now(timezone.utc),
        ))
        count += 1

    await db.flush()
    logger.info(f"迁移完成: {count} 条消息 -> 会话 '{legacy_id}'")

    migrated_path = history_file.with_suffix(".json.migrated")
    history_file.rename(migrated_path)
    logger.info(f"chat_history.json 已重命名为 {migrated_path.name}")
