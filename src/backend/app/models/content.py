"""Content — post, comment, thread, article, video, image, transcript."""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class Content(Base, ProvenanceMixin):
    __tablename__ = "contents"

    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id"), nullable=True
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=True
    )
    content_type: Mapped[str] = mapped_column(
        String(64), nullable=False, default="post",
        doc="post | comment | thread | article | video | image | transcript",
    )
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)

    # Extracted data
    urls: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    hashtags: Mapped[list | None] = mapped_column(ARRAY(String(256)), nullable=True)
    mentions: Mapped[list | None] = mapped_column(ARRAY(String(256)), nullable=True)
    domains: Mapped[list | None] = mapped_column(ARRAY(String(256)), nullable=True)

    # Engagement
    like_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reply_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    repost_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    view_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Embeddings and classification
    embedding: Mapped[list | None] = mapped_column(
        ARRAY(Float), nullable=True, doc="Dense vector for semantic search"
    )
    topics: Mapped[list | None] = mapped_column(ARRAY(String(128)), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_labels: Mapped[list | None] = mapped_column(ARRAY(String(64)), nullable=True)
    is_duplicate: Mapped[bool | None] = mapped_column(default=False)
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Thread context
    parent_content_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contents.id"), nullable=True
    )
    thread_root_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    source = relationship("Source", back_populates="contents")
    actor = relationship("Actor", back_populates="contents")
    media_assets = relationship("MediaAsset", back_populates="content", lazy="selectin")
    claims = relationship("Claim", back_populates="content", lazy="selectin")
    parent = relationship("Content", remote_side="Content.id", foreign_keys=[parent_content_id])
