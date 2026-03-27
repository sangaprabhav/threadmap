"""Entity — person, org, product, location, event."""

from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class Entity(Base, ProvenanceMixin):
    __tablename__ = "entities"

    entity_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True,
        doc="person | org | product | location | event | concept",
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    canonical_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    aliases: Mapped[list | None] = mapped_column(ARRAY(String(512)), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Identifiers
    wikidata_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    external_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Geo
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(4), nullable=True)

    # Stats
    mention_count: Mapped[int | None] = mapped_column(default=0)
    content_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    embedding: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
