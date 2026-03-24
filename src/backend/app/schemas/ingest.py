"""Ingest schemas for manual evidence submission."""

from pydantic import BaseModel


class IngestURLRequest(BaseModel):
    url: str
    title: str | None = None
    text: str | None = None
    content_type: str = "post"
    actor_handle: str | None = None


class IngestTextRequest(BaseModel):
    text: str
    title: str | None = None
    actor_handle: str | None = None
    platform: str | None = None


class IngestCSVRequest(BaseModel):
    content: str
    text_column: str = "text"
    url_column: str = "url"


class IngestResponse(BaseModel):
    event_count: int
    message: str
