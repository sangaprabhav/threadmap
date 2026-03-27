"""Actor — account, channel, domain owner, org, person."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class Actor(Base, ProvenanceMixin):
    __tablename__ = "actors"

    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id"), nullable=True
    )
    actor_type: Mapped[str] = mapped_column(
        String(64), nullable=False, default="account",
        doc="account | channel | domain_owner | org | person",
    )
    handle: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_phash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True, doc="Perceptual hash for cross-platform matching"
    )
    profile_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_links: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    follower_count: Mapped[int | None] = mapped_column(nullable=True)
    following_count: Mapped[int | None] = mapped_column(nullable=True)
    account_created_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language_codes: Mapped[list | None] = mapped_column(ARRAY(String(8)), nullable=True)
    tags: Mapped[list | None] = mapped_column(ARRAY(String(128)), nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    source = relationship("Source", back_populates="actors")
    contents = relationship("Content", back_populates="actor", lazy="selectin")
