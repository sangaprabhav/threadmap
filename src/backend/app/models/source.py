"""Source — platform, URL, collector, auth mode, legality."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class Source(Base, ProvenanceMixin):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(256), nullable=False)
    platform_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True,
        doc="bluesky | x | reddit | youtube | rss | web | manual | telegram | mastodon",
    )
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    auth_mode: Mapped[str | None] = mapped_column(
        String(64), nullable=True, doc="api_key | oauth2 | firehose | none"
    )
    collection_mode: Mapped[str] = mapped_column(
        String(64), nullable=False, default="query",
        doc="streaming | query | backfill | manual",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    legal_basis: Mapped[str | None] = mapped_column(
        String(256), nullable=True, doc="ToS-compliant | research_exemption | public_api"
    )
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    actors = relationship("Actor", back_populates="source", lazy="selectin")
    contents = relationship("Content", back_populates="source", lazy="selectin")
