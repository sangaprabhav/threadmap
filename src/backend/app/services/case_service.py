"""Case service — investigation management."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case


async def list_cases(
    db: AsyncSession,
    status: str | None = None,
    priority: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Case], int]:
    query = select(Case)
    count_query = select(func.count(Case.id))
    conditions = []

    if status:
        conditions.append(Case.status == status)
    if priority:
        conditions.append(Case.priority == priority)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    total = (await db.execute(count_query)).scalar() or 0
    results = (
        await db.execute(
            query.order_by(Case.updated_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return results, total


async def get_case(db: AsyncSession, case_id: uuid.UUID) -> Case | None:
    return (await db.execute(select(Case).where(Case.id == case_id))).scalar_one_or_none()


async def create_case(db: AsyncSession, **kwargs) -> Case:
    case = Case(**kwargs)
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case


async def update_case(db: AsyncSession, case_id: uuid.UUID, **kwargs) -> Case | None:
    case = await get_case(db, case_id)
    if not case:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(case, key):
            setattr(case, key, value)
    await db.commit()
    await db.refresh(case)
    return case


async def add_case_note(
    db: AsyncSession, case_id: uuid.UUID, text: str, note_type: str = "general", author_id: uuid.UUID | None = None
) -> Case | None:
    case = await get_case(db, case_id)
    if not case:
        return None

    notes = case.notes or []
    notes.append({
        "text": text,
        "type": note_type,
        "author_id": str(author_id) if author_id else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    case.notes = notes
    await db.commit()
    await db.refresh(case)
    return case
