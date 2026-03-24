"""Claim — extracted assertion from content."""

import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class Claim(Base, ProvenanceMixin):
    __tablename__ = "claims"

    content_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contents.id"), nullable=True
    )
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("narrative_clusters.id"), nullable=True
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_form: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="Normalized/canonicalized version of the claim"
    )
    claim_type: Mapped[str | None] = mapped_column(
        String(64), nullable=True, doc="factual | opinion | prediction | call_to_action"
    )
    subjects: Mapped[list | None] = mapped_column(ARRAY(String(256)), nullable=True)
    objects: Mapped[list | None] = mapped_column(ARRAY(String(256)), nullable=True)
    verbs: Mapped[list | None] = mapped_column(ARRAY(String(128)), nullable=True)

    # Propagation tracking
    first_seen_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    occurrence_count: Mapped[int | None] = mapped_column(default=1)
    platforms_seen: Mapped[list | None] = mapped_column(ARRAY(String(64)), nullable=True)

    # Confidence
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    match_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    embedding: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    content = relationship("Content", back_populates="claims")
    cluster = relationship("NarrativeCluster", back_populates="claims")
