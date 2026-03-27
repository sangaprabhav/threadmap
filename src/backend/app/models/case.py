"""Case — analyst-owned investigation object."""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class Case(Base, ProvenanceMixin):
    __tablename__ = "cases"

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="open", index=True,
        doc="open | in_progress | review | closed | archived",
    )
    priority: Mapped[str] = mapped_column(
        String(32), nullable=False, default="medium",
        doc="critical | high | medium | low",
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Linked objects
    content_ids: Mapped[list | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    actor_ids: Mapped[list | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    entity_ids: Mapped[list | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    cluster_ids: Mapped[list | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)

    # Classification
    tags: Mapped[list | None] = mapped_column(ARRAY(String(128)), nullable=True)
    category: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Notes and timeline
    notes: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, doc="List of timestamped analyst notes"
    )
    timeline: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, doc="Structured investigation timeline"
    )

    # Export
    briefing: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    alerts = relationship("Alert", back_populates="case", lazy="selectin")
