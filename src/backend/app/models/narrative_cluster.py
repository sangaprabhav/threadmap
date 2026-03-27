"""NarrativeCluster — semantically related claims/content."""

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class NarrativeCluster(Base, ProvenanceMixin):
    __tablename__ = "narrative_clusters"

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="active",
        doc="active | dormant | archived | escalated",
    )

    # Temporal bounds
    first_seen_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_seen_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    peak_velocity_at: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Scale
    content_count: Mapped[int | None] = mapped_column(Integer, default=0)
    actor_count: Mapped[int | None] = mapped_column(Integer, default=0)
    platform_count: Mapped[int | None] = mapped_column(Integer, default=0)
    platforms: Mapped[list | None] = mapped_column(ARRAY(String(64)), nullable=True)

    # Classification
    topics: Mapped[list | None] = mapped_column(ARRAY(String(128)), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    coordination_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Centroid embedding
    centroid_embedding: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    keywords: Mapped[list | None] = mapped_column(ARRAY(String(128)), nullable=True)

    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    claims = relationship("Claim", back_populates="cluster", lazy="selectin")
