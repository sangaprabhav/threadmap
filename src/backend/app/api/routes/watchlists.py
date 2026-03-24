"""Watchlist API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.watchlist import (
    WatchlistOut, WatchlistCreateRequest,
    WatchlistEntryOut, WatchlistEntryCreateRequest,
)
from app.schemas.common import PaginatedResponse
from app.services import watchlist_service

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.get("", response_model=PaginatedResponse)
async def list_watchlists(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await watchlist_service.list_watchlists(db, offset=offset, limit=limit)
    return PaginatedResponse(
        items=[WatchlistOut.model_validate(i) for i in items],
        total=total, offset=offset, limit=limit,
    )


@router.post("", response_model=WatchlistOut)
async def create_watchlist(req: WatchlistCreateRequest, db: AsyncSession = Depends(get_db)):
    wl = await watchlist_service.create_watchlist(
        db,
        name=req.name,
        description=req.description,
        watch_type=req.watch_type,
        alert_on_match=req.alert_on_match,
        platforms=req.platforms,
    )
    return wl


@router.get("/{watchlist_id}", response_model=WatchlistOut)
async def get_watchlist(watchlist_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    wl = await watchlist_service.get_watchlist(db, watchlist_id)
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return wl


@router.post("/{watchlist_id}/entries", response_model=WatchlistEntryOut)
async def add_entry(
    watchlist_id: uuid.UUID,
    req: WatchlistEntryCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    entry = await watchlist_service.add_entry(
        db, watchlist_id=watchlist_id, value=req.value, entry_type=req.entry_type,
    )
    return entry


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await watchlist_service.delete_entry(db, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"deleted": True}
