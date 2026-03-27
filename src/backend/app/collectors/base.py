"""Base collector — common interface for all collection modes."""

import abc
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from pydantic import BaseModel, Field


class RawEvent(BaseModel):
    """Canonical raw event emitted by any collector before enrichment."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str
    collection_mode: str  # streaming | query | backfill | manual
    collector_version: str = "0.1.0"

    # Provenance
    source_native_id: str | None = None
    source_url: str | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observed_at: datetime | None = None

    # Content
    content_type: str = "post"  # post | comment | article | video | image
    text: str | None = None
    title: str | None = None
    media_urls: list[str] = Field(default_factory=list)

    # Actor
    actor_handle: str | None = None
    actor_display_name: str | None = None
    actor_avatar_url: str | None = None
    actor_profile_url: str | None = None
    actor_native_id: str | None = None

    # Engagement
    like_count: int | None = None
    reply_count: int | None = None
    repost_count: int | None = None
    view_count: int | None = None

    # Thread
    parent_native_id: str | None = None
    thread_root_native_id: str | None = None

    # Raw
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class BaseCollector(abc.ABC):
    """Abstract base for all collectors."""

    platform: str
    collection_mode: str

    @abc.abstractmethod
    async def collect(self, **kwargs) -> AsyncIterator[RawEvent]:
        """Yield raw events from this source."""
        ...

    @abc.abstractmethod
    async def healthcheck(self) -> bool:
        """Return True if the collector can reach its source."""
        ...


class StreamingCollector(BaseCollector):
    """Base for real-time streaming connectors."""

    collection_mode = "streaming"

    @abc.abstractmethod
    async def connect(self) -> None:
        """Establish the streaming connection."""
        ...

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """Gracefully close the stream."""
        ...


class QueryCollector(BaseCollector):
    """Base for query/backfill connectors."""

    collection_mode = "query"

    @abc.abstractmethod
    async def search(self, query: str, **kwargs) -> AsyncIterator[RawEvent]:
        """Search the source for matching content."""
        ...
