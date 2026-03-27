"""Alert — machine-generated candidate signal."""

import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class Alert(Base, ProvenanceMixin):
    __tablename__ = "alerts"

    alert_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True,
        doc="spike | new_actor | narrative_shift | coordination | risk | watchlist_match",
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="new", index=True,
        doc="new | triaged | confirmed | dismissed | escalated",
    )
    priority: Mapped[str] = mapped_column(
        String(32), nullable=False, default="medium",
        doc="critical | high | medium | low | info",
    )

    # Decomposed confidence
    source_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    identity_match_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    claim_match_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    coordination_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_priority_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # References
    content_ids: Mapped[list | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    actor_ids: Mapped[list | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    entity_ids: Mapped[list | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("narrative_clusters.id"), nullable=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True
    )
    watchlist_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Analyst action
    triaged_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    triage_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    analyst_feedback: Mapped[str | None] = mapped_column(
        String(64), nullable=True, doc="confirmed | dismissed | needs_review"
    )

    evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    case = relationship("Case", back_populates="alerts")
