"""Provenance mixin — non-negotiable lineage tracking for every intelligence object.

Every analytic conclusion is reproducible from:
  - original source ID / URL
  - collection timestamp (when we fetched it)
  - observed timestamp (when source says it happened)
  - normalized timestamp (UTC canonical)
  - transformation chain (list of enrichment steps applied)
  - model version (which ML model produced the enrichment)
  - prompt/template version
  - confidence and rationale
  - evidence attachments (S3 keys)
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column


class ProvenanceMixin:
    """Mixin that adds provenance columns to any model."""

    # Origin
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    source_native_id: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    platform: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Timestamps
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    normalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Transformation lineage
    transformation_chain: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    collector_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Confidence
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Evidence
    evidence_keys: Mapped[list | None] = mapped_column(
        ARRAY(Text), nullable=True, default=list, doc="S3 object keys for raw evidence"
    )
    raw_payload: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, doc="Original API response, preserved immutably"
    )
