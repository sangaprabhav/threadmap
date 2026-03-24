"""Brief API routes — daily intelligence brief generation."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import brief_service

router = APIRouter(prefix="/briefs", tags=["briefs"])


@router.get("/daily")
async def get_daily_brief(
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """Generate a daily intelligence brief.

    Returns a structured brief with provenance-linked evidence.
    Every headline opens into evidence.
    """
    return await brief_service.generate_daily_brief(db, hours=hours)
