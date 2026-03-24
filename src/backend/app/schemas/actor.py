"""Actor schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ActorOut(BaseModel):
    id: uuid.UUID
    platform: str | None = None
    actor_type: str
    handle: str | None = None
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    profile_url: str | None = None
    follower_count: int | None = None
    following_count: int | None = None
    tags: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ActorDossier(BaseModel):
    """Entity dossier — comprehensive view of an actor."""
    actor: ActorOut
    content_count: int = 0
    platforms: list[str] = []
    recent_content: list[dict] = []
    associated_entities: list[dict] = []
    associated_claims: list[dict] = []
    activity_timeline: list[dict] = []
    risk_summary: dict = {}
    cross_platform_matches: list[dict] = []
