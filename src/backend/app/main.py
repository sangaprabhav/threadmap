"""ThreadMap — Event-native intelligence operating system.

Main FastAPI application. All routes mounted here.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health, content, alerts, cases, watchlists, ingest, briefs

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("threadmap.starting", version="0.1.0")
    yield
    # Shutdown
    try:
        from app.events.producer import shutdown_producer
        await shutdown_producer()
    except Exception:
        pass
    logger.info("threadmap.stopped")


app = FastAPI(
    title="ThreadMap",
    description="Event-native intelligence operating system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(content.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(cases.router, prefix=settings.api_prefix)
app.include_router(watchlists.router, prefix=settings.api_prefix)
app.include_router(ingest.router, prefix=settings.api_prefix)
app.include_router(briefs.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {
        "name": "ThreadMap",
        "version": "0.1.0",
        "description": "Event-native intelligence operating system",
        "docs": f"{settings.api_prefix}/docs",
    }
