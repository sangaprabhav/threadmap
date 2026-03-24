"""Manual evidence ingest — URLs, screenshots, PDFs, CSV/JSON, watchlists.

The fourth lane of the collection fabric: analyst-supplied evidence.
"""

import csv
import io
import json
import structlog
from datetime import datetime, timezone
from typing import AsyncIterator

from app.collectors.base import BaseCollector, RawEvent

logger = structlog.get_logger()


class ManualIngestCollector(BaseCollector):
    platform = "manual"
    collection_mode = "manual"

    async def healthcheck(self) -> bool:
        return True

    async def collect(self, **kwargs) -> AsyncIterator[RawEvent]:
        """Route to the appropriate ingest method."""
        ingest_type = kwargs.get("ingest_type", "url")
        if ingest_type == "url":
            async for event in self.ingest_url(kwargs.get("url", "")):
                yield event
        elif ingest_type == "text":
            async for event in self.ingest_text(kwargs.get("text", ""), **kwargs):
                yield event
        elif ingest_type == "csv":
            async for event in self.ingest_csv(kwargs.get("content", ""), **kwargs):
                yield event
        elif ingest_type == "json":
            async for event in self.ingest_json(kwargs.get("content", ""), **kwargs):
                yield event

    async def ingest_url(self, url: str, **kwargs) -> AsyncIterator[RawEvent]:
        """Ingest a single URL as evidence."""
        yield RawEvent(
            platform="manual",
            collection_mode="manual",
            source_url=url,
            source_native_id=url,
            collected_at=datetime.now(timezone.utc),
            content_type=kwargs.get("content_type", "post"),
            text=kwargs.get("text", ""),
            title=kwargs.get("title", ""),
            raw_payload={"ingest_type": "url", "url": url, **kwargs},
        )

    async def ingest_text(self, text: str, **kwargs) -> AsyncIterator[RawEvent]:
        """Ingest free-form text as evidence."""
        yield RawEvent(
            platform="manual",
            collection_mode="manual",
            collected_at=datetime.now(timezone.utc),
            content_type="post",
            text=text,
            title=kwargs.get("title"),
            actor_handle=kwargs.get("actor_handle"),
            raw_payload={"ingest_type": "text"},
        )

    async def ingest_csv(self, content: str, **kwargs) -> AsyncIterator[RawEvent]:
        """Ingest rows from a CSV as individual events."""
        reader = csv.DictReader(io.StringIO(content))
        text_col = kwargs.get("text_column", "text")
        url_col = kwargs.get("url_column", "url")

        for row in reader:
            yield RawEvent(
                platform="manual",
                collection_mode="manual",
                collected_at=datetime.now(timezone.utc),
                content_type="post",
                text=row.get(text_col, ""),
                source_url=row.get(url_col),
                source_native_id=row.get(url_col) or row.get("id"),
                actor_handle=row.get("author") or row.get("handle") or row.get("username"),
                raw_payload={"ingest_type": "csv", "row": dict(row)},
            )

    async def ingest_json(self, content: str, **kwargs) -> AsyncIterator[RawEvent]:
        """Ingest items from a JSON array."""
        try:
            items = json.loads(content)
            if isinstance(items, dict):
                items = [items]
        except json.JSONDecodeError as e:
            logger.error("manual.json.parse_error", error=str(e))
            return

        for item in items:
            yield RawEvent(
                platform="manual",
                collection_mode="manual",
                collected_at=datetime.now(timezone.utc),
                content_type=item.get("content_type", "post"),
                text=item.get("text", ""),
                title=item.get("title"),
                source_url=item.get("url") or item.get("source_url"),
                source_native_id=item.get("id") or item.get("source_native_id"),
                actor_handle=item.get("author") or item.get("actor_handle"),
                raw_payload={"ingest_type": "json", "item": item},
            )
