"""Alert service — create, triage, and manage alerts."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert


async def list_alerts(
    db: AsyncSession,
    status: str | None = None,
    priority: str | None = None,
    alert_type: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Alert], int]:
    query = select(Alert)
    count_query = select(func.count(Alert.id))
    conditions = []

    if status:
        conditions.append(Alert.status == status)
    if priority:
        conditions.append(Alert.priority == priority)
    if alert_type:
        conditions.append(Alert.alert_type == alert_type)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    total = (await db.execute(count_query)).scalar() or 0
    results = (
        await db.execute(
            query.order_by(Alert.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return results, total


async def get_alert(db: AsyncSession, alert_id: uuid.UUID) -> Alert | None:
    return (await db.execute(select(Alert).where(Alert.id == alert_id))).scalar_one_or_none()


async def create_alert(db: AsyncSession, **kwargs) -> Alert:
    alert = Alert(**kwargs)
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def triage_alert(
    db: AsyncSession,
    alert_id: uuid.UUID,
    status: str,
    feedback: str | None = None,
    notes: str | None = None,
    triaged_by: uuid.UUID | None = None,
    case_id: uuid.UUID | None = None,
) -> Alert | None:
    alert = await get_alert(db, alert_id)
    if not alert:
        return None

    alert.status = status
    alert.analyst_feedback = feedback
    alert.triage_notes = notes
    alert.triaged_by = triaged_by
    if case_id:
        alert.case_id = case_id
    await db.commit()
    await db.refresh(alert)
    return alert


async def get_alert_stats(db: AsyncSession) -> dict:
    by_status = (
        await db.execute(
            select(Alert.status, func.count(Alert.id)).group_by(Alert.status)
        )
    ).all()
    by_priority = (
        await db.execute(
            select(Alert.priority, func.count(Alert.id)).group_by(Alert.priority)
        )
    ).all()
    return {
        "by_status": {s: c for s, c in by_status},
        "by_priority": {p: c for p, c in by_priority},
    }
