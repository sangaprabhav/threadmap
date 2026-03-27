"""X (Twitter) collector — search/stream via official API v2."""

import structlog
import httpx
from datetime import datetime, timezone
from typing import AsyncIterator

from app.collectors.base import QueryCollector, RawEvent
from app.core.config import settings

logger = structlog.get_logger()

X_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
X_TWEET_FIELDS = "id,text,created_at,author_id,public_metrics,referenced_tweets,entities,attachments"
X_USER_FIELDS = "id,name,username,profile_image_url,url"
X_EXPANSIONS = "author_id,attachments.media_keys,referenced_tweets.id"
X_MEDIA_FIELDS = "media_key,type,url,preview_image_url"


class XSearchCollector(QueryCollector):
    platform = "x"

    def __init__(self):
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {settings.x_bearer_token}"},
            timeout=30.0,
        )

    async def healthcheck(self) -> bool:
        if not settings.x_bearer_token:
            return False
        try:
            resp = await self._client.get(
                X_SEARCH_URL,
                params={"query": "test", "max_results": 10},
            )
            return resp.status_code in (200, 429)  # 429 = rate limited but reachable
        except httpx.HTTPError:
            return False

    async def collect(self, **kwargs) -> AsyncIterator[RawEvent]:
        async for event in self.search(kwargs.get("query", ""), **kwargs):
            yield event

    async def search(self, query: str, **kwargs) -> AsyncIterator[RawEvent]:
        if not settings.x_bearer_token:
            logger.warning("x.search.no_bearer_token")
            return

        max_results = kwargs.get("max_results", 100)
        next_token = None

        while True:
            params = {
                "query": query,
                "max_results": min(max_results, 100),
                "tweet.fields": X_TWEET_FIELDS,
                "user.fields": X_USER_FIELDS,
                "expansions": X_EXPANSIONS,
                "media.fields": X_MEDIA_FIELDS,
            }
            if next_token:
                params["next_token"] = next_token

            try:
                resp = await self._client.get(X_SEARCH_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as e:
                logger.error("x.search.error", error=str(e))
                break

            # Build lookup maps
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            media = {m["media_key"]: m for m in data.get("includes", {}).get("media", [])}

            for tweet in data.get("data", []):
                yield self._parse_tweet(tweet, users, media)

            meta = data.get("meta", {})
            next_token = meta.get("next_token")
            if not next_token or meta.get("result_count", 0) == 0:
                break

    def _parse_tweet(self, tweet: dict, users: dict, media: dict) -> RawEvent:
        author_id = tweet.get("author_id", "")
        author = users.get(author_id, {})
        metrics = tweet.get("public_metrics", {})

        # Media URLs
        media_urls = []
        for key in tweet.get("attachments", {}).get("media_keys", []):
            m = media.get(key, {})
            url = m.get("url") or m.get("preview_image_url")
            if url:
                media_urls.append(url)

        # Thread context
        parent_id = None
        for ref in tweet.get("referenced_tweets", []):
            if ref["type"] in ("replied_to", "quoted"):
                parent_id = ref["id"]
                break

        created_at = tweet.get("created_at")
        observed_at = None
        if created_at:
            try:
                observed_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except ValueError:
                pass

        return RawEvent(
            platform="x",
            collection_mode="query",
            source_native_id=tweet["id"],
            source_url=f"https://x.com/{author.get('username', '_')}/status/{tweet['id']}",
            collected_at=datetime.now(timezone.utc),
            observed_at=observed_at,
            content_type="post",
            text=tweet.get("text", ""),
            media_urls=media_urls,
            actor_handle=author.get("username"),
            actor_display_name=author.get("name"),
            actor_avatar_url=author.get("profile_image_url"),
            actor_native_id=author_id,
            actor_profile_url=f"https://x.com/{author.get('username', '')}",
            like_count=metrics.get("like_count"),
            reply_count=metrics.get("reply_count"),
            repost_count=metrics.get("retweet_count"),
            view_count=metrics.get("impression_count"),
            parent_native_id=parent_id,
            raw_payload=tweet,
        )
