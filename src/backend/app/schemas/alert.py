"""Alert schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: uuid.UUID
    alert_type: str
    title: str
    summary: str | None = None
    status: str
    priority: str
    source_confidence: float | None = None
    extraction_confidence: float | None = None
    overall_priority_score: float | None = None
    content_ids: list[uuid.UUID] | None = None
    actor_ids: list[uuid.UUID] | None = None
    case_id: uuid.UUID | None = None
    analyst_feedback: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertTriageRequest(BaseModel):
    status: str  # triaged | confirmed | dismissed | escalated
    feedback: str | None = None  # confirmed | dismissed | needs_review
    triage_notes: str | None = None
    case_id: uuid.UUID | None = None


class AlertCreateRequest(BaseModel):
    alert_type: str
    title: str
    summary: str | None = None
    priority: str = "medium"
    content_ids: list[uuid.UUID] | None = None
    actor_ids: list[uuid.UUID] | None = None
    evidence: dict | None = None
