"""
Migration service — migrate legacy chat_history.json to MySQL.
"""
import logging
import json as _json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

HISTORY_FILE = Path(__file__).parent.parent / "chat_history.json"


async def migrate_chat_history_json(db: AsyncSession) -> None:
    """Migrate chat_history.json to MySQL."""
    if not HISTORY_FILE.exists():
        return

    logger.info("检测到 chat_history.json，开始迁移到 MySQL...")
    try:
        raw = _json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (_json.JSONDecodeError, Exception) as e:
        logger.warning(f"读取 chat_history.json 失败: {e}，跳过迁移")
        return

    if not raw or not isinstance(raw, list):
        logger.info("chat_history.json 为空，跳过迁移")
        return

    from models import SessionModel, MessageModel, MessageRole
    legacy_id = "legacy-" + uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    db.add(SessionModel(
        id=legacy_id,
        name="历史记录",
        created_at=now,
        updated_at=now,
    ))
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

    migrated_path = HISTORY_FILE.with_suffix(".json.migrated")
    HISTORY_FILE.rename(migrated_path)
    logger.info(f"chat_history.json 已重命名为 {migrated_path.name}")
