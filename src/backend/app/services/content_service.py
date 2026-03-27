"""Content service — CRUD and search for intelligence content."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.actor import Actor
from app.schemas.content import ContentSearchParams


async def search_content(db: AsyncSession, params: ContentSearchParams) -> tuple[list[Content], int]:
    """Search content with filters."""
    query = select(Content)
    count_query = select(func.count(Content.id))
    conditions = []

    if params.platform:
        conditions.append(Content.platform == params.platform)
    if params.content_type:
        conditions.append(Content.content_type == params.content_type)
    if params.language:
        conditions.append(Content.language == params.language)
    if params.min_risk_score is not None:
        conditions.append(Content.risk_score >= params.min_risk_score)
    if params.start_date:
        conditions.append(Content.collected_at >= params.start_date)
    if params.end_date:
        conditions.append(Content.collected_at <= params.end_date)
    if params.query:
        conditions.append(Content.text.ilike(f"%{params.query}%"))

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    total = (await db.execute(count_query)).scalar() or 0
    results = (
        await db.execute(
            query.order_by(Content.collected_at.desc())
            .offset(params.offset)
            .limit(params.limit)
        )
    ).scalars().all()

    return results, total


async def get_content_by_id(db: AsyncSession, content_id: uuid.UUID) -> Content | None:
    return (await db.execute(select(Content).where(Content.id == content_id))).scalar_one_or_none()


async def get_live_stream(db: AsyncSession, limit: int = 50, platform: str | None = None) -> list[Content]:
    """Get the most recent content items for the live stream view."""
    query = select(Content).order_by(Content.collected_at.desc()).limit(limit)
    if platform:
        query = query.where(Content.platform == platform)
    return (await db.execute(query)).scalars().all()


async def get_content_stats(db: AsyncSession) -> dict:
    """Get aggregate content statistics."""
    total = (await db.execute(select(func.count(Content.id)))).scalar() or 0
    by_platform = (
        await db.execute(
            select(Content.platform, func.count(Content.id))
            .group_by(Content.platform)
        )
    ).all()
    by_type = (
        await db.execute(
            select(Content.content_type, func.count(Content.id))
            .group_by(Content.content_type)
        )
    ).all()

    return {
        "total": total,
        "by_platform": {p: c for p, c in by_platform if p},
        "by_type": {t: c for t, c in by_type if t},
    }
