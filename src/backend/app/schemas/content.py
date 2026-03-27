"""Content schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ContentOut(BaseModel):
    id: uuid.UUID
    source_url: str | None = None
    platform: str | None = None
    content_type: str
    text: str | None = None
    title: str | None = None
    language: str | None = None
    urls: list[str] | None = None
    hashtags: list[str] | None = None
    mentions: list[str] | None = None
    domains: list[str] | None = None
    like_count: int | None = None
    reply_count: int | None = None
    repost_count: int | None = None
    view_count: int | None = None
    topics: list[str] | None = None
    risk_score: float | None = None
    risk_labels: list[str] | None = None
    is_duplicate: bool | None = None
    collected_at: datetime | None = None
    observed_at: datetime | None = None
    created_at: datetime
    actor_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class ContentSearchParams(BaseModel):
    query: str | None = None
    platform: str | None = None
    content_type: str | None = None
    language: str | None = None
    min_risk_score: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    offset: int = 0
    limit: int = 50
