"""Watchlist schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class WatchlistOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    watch_type: str
    is_active: bool
    alert_on_match: bool
    platforms: list[str] | None = None
    entry_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class WatchlistCreateRequest(BaseModel):
    name: str
    description: str | None = None
    watch_type: str = "keyword"
    alert_on_match: bool = True
    platforms: list[str] | None = None


class WatchlistEntryOut(BaseModel):
    id: uuid.UUID
    value: str
    entry_type: str
    is_active: bool
    match_count: int | None = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class WatchlistEntryCreateRequest(BaseModel):
    value: str
    entry_type: str = "keyword"  # keyword | handle | domain | hashtag | regex
