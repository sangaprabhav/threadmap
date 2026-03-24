"""Reddit collector — search and listing via official API."""

import structlog
import httpx
from datetime import datetime, timezone
from typing import AsyncIterator

from app.collectors.base import QueryCollector, RawEvent
from app.core.config import settings

logger = structlog.get_logger()

REDDIT_AUTH_URL = "https://www.reddit.com/api/v1/access_token"
REDDIT_API_BASE = "https://oauth.reddit.com"


class RedditCollector(QueryCollector):
    platform = "reddit"

    def __init__(self):
        self._token: str | None = None
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _authenticate(self) -> None:
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            logger.warning("reddit.no_credentials")
            return
        resp = await self._client.post(
            REDDIT_AUTH_URL,
            auth=(settings.reddit_client_id, settings.reddit_client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": "ThreadMap/0.1"},
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        self._client.headers["Authorization"] = f"Bearer {self._token}"
        self._client.headers["User-Agent"] = "ThreadMap/0.1"

    async def healthcheck(self) -> bool:
        if not settings.reddit_client_id:
            return False
        try:
            await self._authenticate()
            return self._token is not None
        except httpx.HTTPError:
            return False

    async def collect(self, **kwargs) -> AsyncIterator[RawEvent]:
        async for event in self.search(kwargs.get("query", ""), **kwargs):
            yield event

    async def search(self, query: str, **kwargs) -> AsyncIterator[RawEvent]:
        if not self._token:
            await self._authenticate()
        if not self._token:
            return

        subreddit = kwargs.get("subreddit")
        sort = kwargs.get("sort", "new")
        limit = kwargs.get("limit", 100)
        after = kwargs.get("after")

        if subreddit:
            url = f"{REDDIT_API_BASE}/r/{subreddit}/search"
        else:
            url = f"{REDDIT_API_BASE}/search"

        params = {
            "q": query,
            "sort": sort,
            "limit": min(limit, 100),
            "restrict_sr": "true" if subreddit else "false",
            "type": "link",
        }
        if after:
            params["after"] = after

        try:
            resp = await self._client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            logger.error("reddit.search.error", error=str(e))
            return

        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            yield self._parse_post(post)

    def _parse_post(self, post: dict) -> RawEvent:
        created_utc = post.get("created_utc")
        observed_at = (
            datetime.fromtimestamp(created_utc, tz=timezone.utc) if created_utc else None
        )

        media_urls = []
        if post.get("url", "").endswith((".jpg", ".png", ".gif", ".webp")):
            media_urls.append(post["url"])
        if preview := post.get("preview", {}).get("images", []):
            for img in preview:
                if src := img.get("source", {}).get("url"):
                    media_urls.append(src.replace("&amp;", "&"))

        text = post.get("selftext", "") or ""
        title = post.get("title", "")

        return RawEvent(
            platform="reddit",
            collection_mode="query",
            source_native_id=post.get("id", ""),
            source_url=f"https://reddit.com{post.get('permalink', '')}",
            collected_at=datetime.now(timezone.utc),
            observed_at=observed_at,
            content_type="post",
            text=text,
            title=title,
            media_urls=media_urls,
            actor_handle=post.get("author"),
            actor_native_id=post.get("author_fullname"),
            like_count=post.get("ups"),
            reply_count=post.get("num_comments"),
            raw_payload=post,
        )
