"""Metrics router — observability dashboard API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.observability_service import get_metrics, get_request_logs

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def metrics(days: int = Query(7, ge=1, le=90), db: AsyncSession = Depends(get_db)):
    return await get_metrics(db, days=days)


@router.get("/metrics/requests")
async def request_logs(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    return await get_request_logs(db, page=page, limit=limit)
