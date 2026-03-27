"""Watchlist service — manage monitoring targets."""

import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.watchlist import Watchlist, WatchlistEntry


async def list_watchlists(db: AsyncSession, offset: int = 0, limit: int = 50) -> tuple[list[Watchlist], int]:
    total = (await db.execute(select(func.count(Watchlist.id)))).scalar() or 0
    results = (
        await db.execute(
            select(Watchlist).order_by(Watchlist.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return results, total


async def get_watchlist(db: AsyncSession, watchlist_id: uuid.UUID) -> Watchlist | None:
    return (await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))).scalar_one_or_none()


async def create_watchlist(db: AsyncSession, **kwargs) -> Watchlist:
    wl = Watchlist(**kwargs)
    db.add(wl)
    await db.commit()
    await db.refresh(wl)
    return wl


async def add_entry(db: AsyncSession, watchlist_id: uuid.UUID, value: str, entry_type: str = "keyword") -> WatchlistEntry:
    entry = WatchlistEntry(watchlist_id=watchlist_id, value=value, entry_type=entry_type)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_all_active_entries(db: AsyncSession) -> list[dict]:
    """Get all active watchlist entries for the matcher cache."""
    results = (
        await db.execute(
            select(WatchlistEntry, Watchlist.alert_on_match)
            .join(Watchlist)
            .where(WatchlistEntry.is_active == True)
            .where(Watchlist.is_active == True)
        )
    ).all()

    return [
        {
            "id": str(entry.id),
            "watchlist_id": str(entry.watchlist_id),
            "value": entry.value,
            "entry_type": entry.entry_type,
            "alert_on_match": alert_on_match,
        }
        for entry, alert_on_match in results
    ]


async def delete_entry(db: AsyncSession, entry_id: uuid.UUID) -> bool:
    entry = (await db.execute(select(WatchlistEntry).where(WatchlistEntry.id == entry_id))).scalar_one_or_none()
    if not entry:
        return False
    await db.delete(entry)
    await db.commit()
    return True
