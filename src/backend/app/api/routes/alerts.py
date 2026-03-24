"""Alert API routes — inbox, triage, stats."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.alert import AlertOut, AlertTriageRequest, AlertCreateRequest
from app.schemas.common import PaginatedResponse
from app.services import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=PaginatedResponse)
async def list_alerts(
    status: str | None = None,
    priority: str | None = None,
    alert_type: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await alert_service.list_alerts(
        db, status=status, priority=priority, alert_type=alert_type,
        offset=offset, limit=limit,
    )
    return PaginatedResponse(
        items=[AlertOut.model_validate(i) for i in items],
        total=total, offset=offset, limit=limit,
    )


@router.post("", response_model=AlertOut)
async def create_alert(req: AlertCreateRequest, db: AsyncSession = Depends(get_db)):
    alert = await alert_service.create_alert(
        db,
        alert_type=req.alert_type,
        title=req.title,
        summary=req.summary,
        priority=req.priority,
        content_ids=req.content_ids,
        actor_ids=req.actor_ids,
        evidence=req.evidence,
    )
    return alert


@router.get("/stats")
async def get_alert_stats(db: AsyncSession = Depends(get_db)):
    return await alert_service.get_alert_stats(db)


@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    alert = await alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/triage", response_model=AlertOut)
async def triage_alert(
    alert_id: uuid.UUID,
    req: AlertTriageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Analyst triage action — confirm, dismiss, or escalate."""
    alert = await alert_service.triage_alert(
        db, alert_id,
        status=req.status,
        feedback=req.feedback,
        notes=req.triage_notes,
        case_id=req.case_id,
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
