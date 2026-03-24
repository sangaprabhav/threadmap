"""Bluesky Jetstream collector — real-time streaming via AT Protocol.

Jetstream is Bluesky's lighter streaming layer for filtering/fan-out.
It provides a WebSocket interface that streams repository events in real time.
"""

import json
import structlog
import websockets
from datetime import datetime, timezone
from typing import AsyncIterator

from app.collectors.base import RawEvent, StreamingCollector
from app.core.config import settings

logger = structlog.get_logger()


class BlueskyJetstreamCollector(StreamingCollector):
    platform = "bluesky"

    def __init__(self, wanted_collections: list[str] | None = None):
        self._ws = None
        self._running = False
        # Default to posts (app.bsky.feed.post)
        self.wanted_collections = wanted_collections or ["app.bsky.feed.post"]

    async def connect(self) -> None:
        url = settings.bluesky_firehose_url
        params = "&".join(
            f"wantedCollections={c}" for c in self.wanted_collections
        )
        self._ws = await websockets.connect(f"{url}?{params}")
        self._running = True
        logger.info("bluesky.jetstream.connected", url=url)

    async def disconnect(self) -> None:
        self._running = False
        if self._ws:
            await self._ws.close()
            logger.info("bluesky.jetstream.disconnected")

    async def healthcheck(self) -> bool:
        return self._ws is not None and self._ws.open

    async def collect(self, **kwargs) -> AsyncIterator[RawEvent]:
        if not self._ws:
            await self.connect()

        async for message in self._ws:
            if not self._running:
                break

            try:
                data = json.loads(message)
                event = self._parse_event(data)
                if event:
                    yield event
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("bluesky.jetstream.parse_error", error=str(e))
                continue

    def _parse_event(self, data: dict) -> RawEvent | None:
        """Parse a Jetstream event into a RawEvent."""
        kind = data.get("kind")
        if kind != "commit":
            return None

        commit = data.get("commit", {})
        record = commit.get("record", {})
        did = data.get("did", "")
        rkey = commit.get("rkey", "")

        # Only process creates for now
        if commit.get("operation") != "create":
            return None

        text = record.get("text", "")
        if not text:
            return None

        # Extract media URLs from embeds
        media_urls = []
        embed = record.get("embed", {})
        if embed.get("$type") == "app.bsky.embed.images":
            for img in embed.get("images", []):
                if img_blob := img.get("image", {}).get("ref", {}).get("$link"):
                    media_urls.append(
                        f"https://bsky.social/xrpc/com.atproto.sync.getBlob?did={did}&cid={img_blob}"
                    )

        # Extract reply context
        parent_native_id = None
        thread_root_native_id = None
        reply = record.get("reply", {})
        if reply:
            parent_native_id = reply.get("parent", {}).get("uri")
            thread_root_native_id = reply.get("root", {}).get("uri")

        created_at_str = record.get("createdAt")
        observed_at = None
        if created_at_str:
            try:
                observed_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            except ValueError:
                observed_at = None

        return RawEvent(
            platform="bluesky",
            collection_mode="streaming",
            source_native_id=f"at://{did}/app.bsky.feed.post/{rkey}",
            source_url=f"https://bsky.app/profile/{did}/post/{rkey}",
            collected_at=datetime.now(timezone.utc),
            observed_at=observed_at,
            content_type="post",
            text=text,
            media_urls=media_urls,
            actor_handle=did,
            actor_native_id=did,
            actor_profile_url=f"https://bsky.app/profile/{did}",
            parent_native_id=parent_native_id,
            thread_root_native_id=thread_root_native_id,
            raw_payload=data,
        )
