"""Ingest API routes — manual evidence submission."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.ingest import IngestURLRequest, IngestTextRequest, IngestCSVRequest, IngestResponse
from app.collectors.manual.ingest import ManualIngestCollector

router = APIRouter(prefix="/ingest", tags=["ingest"])

_collector = ManualIngestCollector()


@router.post("/url", response_model=IngestResponse)
async def ingest_url(req: IngestURLRequest, db: AsyncSession = Depends(get_db)):
    """Ingest a URL as evidence."""
    count = 0
    async for _ in _collector.ingest_url(
        req.url, title=req.title, text=req.text,
        content_type=req.content_type, actor_handle=req.actor_handle,
    ):
        count += 1
    return IngestResponse(event_count=count, message=f"Ingested {count} events from URL")


@router.post("/text", response_model=IngestResponse)
async def ingest_text(req: IngestTextRequest, db: AsyncSession = Depends(get_db)):
    """Ingest free-form text as evidence."""
    count = 0
    async for _ in _collector.ingest_text(
        req.text, title=req.title, actor_handle=req.actor_handle,
    ):
        count += 1
    return IngestResponse(event_count=count, message=f"Ingested {count} text events")


@router.post("/csv", response_model=IngestResponse)
async def ingest_csv(req: IngestCSVRequest, db: AsyncSession = Depends(get_db)):
    """Ingest rows from CSV content."""
    count = 0
    async for _ in _collector.ingest_csv(
        req.content, text_column=req.text_column, url_column=req.url_column,
    ):
        count += 1
    return IngestResponse(event_count=count, message=f"Ingested {count} CSV rows")
