"""Edge — connects any two intelligence objects.

Edge types: mention, reply, repost, follows, links_to, same_media,
likely_same_actor, same_claim, temporal_propagation, quotes, embeds,
co_mention, coordination_signal.
"""

import uuid

from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.provenance import ProvenanceMixin


class Edge(Base, ProvenanceMixin):
    __tablename__ = "edges"

    edge_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True,
        doc="mention | reply | repost | follows | links_to | same_media | "
        "likely_same_actor | same_claim | temporal_propagation | quotes | "
        "embeds | co_mention | coordination_signal",
    )
    source_node_type: Mapped[str] = mapped_column(
        String(64), nullable=False,
        doc="actor | content | entity | claim | cluster | media_asset",
    )
    source_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    target_node_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Scored, not binary
    weight: Mapped[float | None] = mapped_column(Float, nullable=True, default=1.0)
    label: Mapped[str | None] = mapped_column(String(256), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Analyst confirmation
    analyst_confirmed: Mapped[bool | None] = mapped_column(default=None)
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
