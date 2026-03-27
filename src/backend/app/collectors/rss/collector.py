"""RSS/News/Web collector — feeds, blogs, forums, news sites."""

import structlog
import httpx
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import AsyncIterator

from app.collectors.base import QueryCollector, RawEvent

logger = structlog.get_logger()


class RSSCollector(QueryCollector):
    platform = "rss"

    def __init__(self):
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "ThreadMap/0.1 (RSS Collector)"},
        )

    async def healthcheck(self) -> bool:
        return True  # RSS doesn't require auth

    async def collect(self, **kwargs) -> AsyncIterator[RawEvent]:
        feed_urls = kwargs.get("feed_urls", [])
        for url in feed_urls:
            async for event in self._parse_feed(url):
                yield event

    async def search(self, query: str, **kwargs) -> AsyncIterator[RawEvent]:
        feed_urls = kwargs.get("feed_urls", [])
        for url in feed_urls:
            async for event in self._parse_feed(url):
                if query.lower() in (event.text or "").lower() or query.lower() in (event.title or "").lower():
                    yield event

    async def _parse_feed(self, url: str) -> AsyncIterator[RawEvent]:
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
        except (httpx.HTTPError, Exception) as e:
            logger.error("rss.fetch.error", url=url, error=str(e))
            return

        feed_title = feed.feed.get("title", url)

        for entry in feed.entries:
            observed_at = None
            if published := entry.get("published"):
                try:
                    observed_at = parsedate_to_datetime(published)
                    if observed_at.tzinfo is None:
                        observed_at = observed_at.replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    pass

            # Extract media
            media_urls = []
            for enc in entry.get("enclosures", []):
                if enc.get("href"):
                    media_urls.append(enc["href"])
            for link in entry.get("links", []):
                if link.get("type", "").startswith("image/"):
                    media_urls.append(link["href"])

            text = entry.get("summary", "") or entry.get("description", "")
            # Strip HTML tags (basic)
            import re
            text = re.sub(r"<[^>]+>", "", text).strip()

            yield RawEvent(
                platform="rss",
                collection_mode="query",
                source_native_id=entry.get("id") or entry.get("link", ""),
                source_url=entry.get("link", ""),
                collected_at=datetime.now(timezone.utc),
                observed_at=observed_at,
                content_type="article",
                text=text,
                title=entry.get("title", ""),
                media_urls=media_urls,
                actor_handle=entry.get("author") or feed_title,
                raw_payload={"entry": {k: str(v) for k, v in entry.items() if isinstance(v, (str, int, float))}},
            )
