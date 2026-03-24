"""Content API routes — live stream, search, detail."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.content import ContentOut, ContentSearchParams
from app.schemas.common import PaginatedResponse
from app.services import content_service

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/stream", response_model=list[ContentOut])
async def get_live_stream(
    limit: int = Query(default=50, le=200),
    platform: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Live event stream — most recent content items."""
    items = await content_service.get_live_stream(db, limit=limit, platform=platform)
    return items


@router.post("/search", response_model=PaginatedResponse)
async def search_content(
    params: ContentSearchParams,
    db: AsyncSession = Depends(get_db),
):
    """Search content with filters."""
    items, total = await content_service.search_content(db, params)
    return PaginatedResponse(
        items=[ContentOut.model_validate(i) for i in items],
        total=total,
        offset=params.offset,
        limit=params.limit,
    )


@router.get("/stats")
async def get_content_stats(db: AsyncSession = Depends(get_db)):
    """Aggregate content statistics."""
    return await content_service.get_content_stats(db)


@router.get("/{content_id}", response_model=ContentOut)
async def get_content(content_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await content_service.get_content_by_id(db, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return item
