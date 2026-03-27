"""Watchlist — analyst-defined monitoring targets."""

import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Watchlist(Base):
    __tablename__ = "watchlists"

    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    watch_type: Mapped[str] = mapped_column(
        String(64), nullable=False, default="keyword",
        doc="keyword | actor | domain | hashtag | url_pattern | entity",
    )
    alert_on_match: Mapped[bool] = mapped_column(Boolean, default=True)
    platforms: Mapped[list | None] = mapped_column(ARRAY(String(64)), nullable=True)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    entries = relationship("WatchlistEntry", back_populates="watchlist", lazy="selectin")


class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"

    watchlist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("watchlists.id"), nullable=False
    )
    value: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    entry_type: Mapped[str] = mapped_column(
        String(64), nullable=False, doc="keyword | handle | domain | hashtag | regex"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    match_count: Mapped[int | None] = mapped_column(default=0)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    watchlist = relationship("Watchlist", back_populates="entries")
