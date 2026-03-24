"""Shared Pydantic schemas for API request/response."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    offset: int = 0
    limit: int = Field(default=50, le=500)


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    offset: int
    limit: int


class ProvenanceOut(BaseModel):
    source_url: str | None = None
    source_native_id: str | None = None
    platform: str | None = None
    collected_at: datetime | None = None
    observed_at: datetime | None = None
    transformation_chain: list[dict] | None = None
    confidence: float | None = None
    confidence_rationale: str | None = None

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    version: str
    collectors: dict[str, bool] = {}
