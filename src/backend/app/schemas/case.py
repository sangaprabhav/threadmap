"""Case schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class CaseOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    priority: str
    assigned_to: uuid.UUID | None = None
    created_by: uuid.UUID | None = None
    tags: list[str] | None = None
    category: str | None = None
    briefing: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseCreateRequest(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    tags: list[str] | None = None
    category: str | None = None
    content_ids: list[uuid.UUID] | None = None
    actor_ids: list[uuid.UUID] | None = None
    entity_ids: list[uuid.UUID] | None = None


class CaseUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assigned_to: uuid.UUID | None = None
    tags: list[str] | None = None
    category: str | None = None


class CaseNoteRequest(BaseModel):
    text: str
    note_type: str = "general"  # general | finding | action | decision
