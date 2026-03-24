"""Health and system status routes."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version="0.1.0",
        collectors={
            "bluesky": True,
            "x": bool(settings.x_bearer_token),
            "reddit": bool(settings.reddit_client_id),
            "youtube": bool(settings.youtube_api_key),
            "rss": True,
            "manual": True,
        },
    )
