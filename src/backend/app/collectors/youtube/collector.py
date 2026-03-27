"""YouTube collector — search, video details, and comments via Data API v3."""

import structlog
import httpx
from datetime import datetime, timezone
from typing import AsyncIterator

from app.collectors.base import QueryCollector, RawEvent
from app.core.config import settings

logger = structlog.get_logger()

YT_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YT_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YT_COMMENTS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"


class YouTubeCollector(QueryCollector):
    platform = "youtube"

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0)

    async def healthcheck(self) -> bool:
        if not settings.youtube_api_key:
            return False
        try:
            resp = await self._client.get(
                YT_SEARCH_URL,
                params={"key": settings.youtube_api_key, "q": "test", "maxResults": 1, "part": "id"},
            )
            return resp.status_code in (200, 403)
        except httpx.HTTPError:
            return False

    async def collect(self, **kwargs) -> AsyncIterator[RawEvent]:
        async for event in self.search(kwargs.get("query", ""), **kwargs):
            yield event

    async def search(self, query: str, **kwargs) -> AsyncIterator[RawEvent]:
        if not settings.youtube_api_key:
            logger.warning("youtube.no_api_key")
            return

        max_results = kwargs.get("max_results", 50)
        page_token = None

        while True:
            params = {
                "key": settings.youtube_api_key,
                "q": query,
                "part": "snippet",
                "type": "video",
                "maxResults": min(max_results, 50),
                "order": "date",
            }
            if page_token:
                params["pageToken"] = page_token

            try:
                resp = await self._client.get(YT_SEARCH_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as e:
                logger.error("youtube.search.error", error=str(e))
                break

            for item in data.get("items", []):
                yield self._parse_search_result(item)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

    async def get_comments(self, video_id: str, **kwargs) -> AsyncIterator[RawEvent]:
        """Fetch comment threads for a video."""
        if not settings.youtube_api_key:
            return

        page_token = None
        while True:
            params = {
                "key": settings.youtube_api_key,
                "videoId": video_id,
                "part": "snippet",
                "maxResults": 100,
                "order": "time",
            }
            if page_token:
                params["pageToken"] = page_token

            try:
                resp = await self._client.get(YT_COMMENTS_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as e:
                logger.error("youtube.comments.error", error=str(e), video_id=video_id)
                break

            for item in data.get("items", []):
                snippet = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                yield RawEvent(
                    platform="youtube",
                    collection_mode="query",
                    source_native_id=item.get("id", ""),
                    source_url=f"https://www.youtube.com/watch?v={video_id}&lc={item.get('id', '')}",
                    collected_at=datetime.now(timezone.utc),
                    observed_at=self._parse_time(snippet.get("publishedAt")),
                    content_type="comment",
                    text=snippet.get("textOriginal", ""),
                    actor_handle=snippet.get("authorDisplayName"),
                    actor_profile_url=snippet.get("authorChannelUrl"),
                    like_count=snippet.get("likeCount"),
                    parent_native_id=video_id,
                    raw_payload=item,
                )

            page_token = data.get("nextPageToken")
            if not page_token:
                break

    def _parse_search_result(self, item: dict) -> RawEvent:
        snippet = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId", "")

        thumbnails = snippet.get("thumbnails", {})
        media_urls = []
        if high := thumbnails.get("high", {}).get("url"):
            media_urls.append(high)

        return RawEvent(
            platform="youtube",
            collection_mode="query",
            source_native_id=video_id,
            source_url=f"https://www.youtube.com/watch?v={video_id}",
            collected_at=datetime.now(timezone.utc),
            observed_at=self._parse_time(snippet.get("publishedAt")),
            content_type="video",
            text=snippet.get("description", ""),
            title=snippet.get("title", ""),
            media_urls=media_urls,
            actor_handle=snippet.get("channelTitle"),
            actor_native_id=snippet.get("channelId"),
            actor_profile_url=f"https://www.youtube.com/channel/{snippet.get('channelId', '')}",
            raw_payload=item,
        )

    @staticmethod
    def _parse_time(ts: str | None) -> datetime | None:
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
