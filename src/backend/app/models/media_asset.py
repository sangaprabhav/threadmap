"""MediaAsset — image, frame, audio, OCR text, video."""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class MediaAsset(Base, ProvenanceMixin):
    __tablename__ = "media_assets"

    content_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contents.id"), nullable=True
    )
    media_type: Mapped[str] = mapped_column(
        String(64), nullable=False, doc="image | video | audio | document | frame"
    )
    original_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    s3_key: Mapped[str | None] = mapped_column(String(512), nullable=True, doc="Object store path")
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Perceptual hashing for cross-platform matching
    phash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    dhash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    ahash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # OCR / ASR
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Visual analysis
    detected_objects: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    detected_text_regions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    exif_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Embedding
    embedding: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Similarity score to known media
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    similar_to_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    content = relationship("Content", back_populates="media_assets")
