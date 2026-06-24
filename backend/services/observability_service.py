"""Observability service — request logging and metrics aggregation."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models import RequestLog

logger = logging.getLogger(__name__)


async def save_request_log(
    db: AsyncSession,
    session_id: str,
    provider_id: Optional[str] = None,
    model_name: Optional[str] = None,
    tokens_in: int = 0,
    tokens_out: int = 0,
    latency_ms: int = 0,
    tool_calls: int = 0,
    tool_names: Optional[list] = None,
    error: Optional[str] = None,
) -> None:
    try:
        db.add(RequestLog(
            session_id=session_id,
            provider_id=provider_id,
            model_name=model_name,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            tool_names=tool_names,
            error=error,
        ))
        await db.flush()
    except Exception as e:
        logger.warning(f"Failed to save request log: {e}")


async def get_metrics(db: AsyncSession, days: int = 7) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Total stats
    result = await db.execute(
        select(
            func.count(RequestLog.id),
            func.coalesce(func.sum(RequestLog.tokens_in + RequestLog.tokens_out), 0),
            func.coalesce(func.avg(RequestLog.latency_ms), 0),
        ).where(RequestLog.created_at >= since)
    )
    total_requests, total_tokens, avg_latency = result.one()

    # Error rate
    result = await db.execute(
        select(func.count(RequestLog.id))
        .where(RequestLog.created_at >= since, RequestLog.error.isnot(None))
    )
    error_count = result.scalar() or 0
    error_rate = round(error_count / total_requests * 100, 2) if total_requests else 0

    # By provider
    result = await db.execute(
        select(
            RequestLog.provider_id,
            func.count(RequestLog.id),
            func.coalesce(func.sum(RequestLog.tokens_in + RequestLog.tokens_out), 0),
            func.coalesce(func.avg(RequestLog.latency_ms), 0),
        )
        .where(RequestLog.created_at >= since, RequestLog.provider_id.isnot(None))
        .group_by(RequestLog.provider_id)
    )
    by_provider = [
        {"provider_id": r[0], "count": r[1], "tokens": r[2] or 0, "avg_latency": round(r[3] or 0, 1)}
        for r in result.all()
    ]

    # By model
    result = await db.execute(
        select(
            RequestLog.model_name,
            func.count(RequestLog.id),
            func.coalesce(func.sum(RequestLog.tokens_in + RequestLog.tokens_out), 0),
        )
        .where(RequestLog.created_at >= since, RequestLog.model_name.isnot(None))
        .group_by(RequestLog.model_name)
    )
    by_model = [
        {"model_name": r[0], "count": r[1], "tokens": r[2] or 0}
        for r in result.all()
    ]

    # Daily trend
    result = await db.execute(
        select(
            func.date(RequestLog.created_at),
            func.count(RequestLog.id),
            func.coalesce(func.sum(RequestLog.tokens_in + RequestLog.tokens_out), 0),
        )
        .where(RequestLog.created_at >= since)
        .group_by(func.date(RequestLog.created_at))
        .order_by(func.date(RequestLog.created_at))
    )
    daily = [
        {"date": str(r[0]), "count": r[1], "tokens": r[2] or 0}
        for r in result.all()
    ]

    return {
        "total_requests": total_requests or 0,
        "total_tokens": total_tokens or 0,
        "avg_latency_ms": round(avg_latency or 0, 1),
        "error_rate": error_rate,
        "by_provider": by_provider,
        "by_model": by_model,
        "daily": daily,
    }


async def get_request_logs(db: AsyncSession, page: int = 1, limit: int = 20) -> dict:
    offset = (page - 1) * limit

    result = await db.execute(
        select(func.count(RequestLog.id))
    )
    total = result.scalar() or 0

    result = await db.execute(
        select(RequestLog)
        .order_by(RequestLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = []
    for r in result.scalars().all():
        items.append({
            "id": r.id,
            "session_id": r.session_id,
            "provider_id": r.provider_id,
            "model_name": r.model_name,
            "tokens_in": r.tokens_in,
            "tokens_out": r.tokens_out,
            "latency_ms": r.latency_ms,
            "tool_calls": r.tool_calls,
            "error": r.error,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })

    return {"items": items, "total": total, "page": page}
