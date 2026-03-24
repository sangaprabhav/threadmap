"""Tests for collector base classes and parsing."""

import pytest
from datetime import datetime, timezone

from app.collectors.base import RawEvent


class TestRawEvent:
    def test_default_fields(self):
        event = RawEvent(platform="test", collection_mode="manual")
        assert event.platform == "test"
        assert event.collection_mode == "manual"
        assert event.event_id is not None
        assert event.collected_at is not None

    def test_full_event(self):
        event = RawEvent(
            platform="bluesky",
            collection_mode="streaming",
            source_native_id="at://did:plc:123/app.bsky.feed.post/abc",
            source_url="https://bsky.app/profile/test/post/abc",
            text="Hello world",
            actor_handle="test.bsky.social",
            actor_display_name="Test User",
            like_count=42,
            raw_payload={"key": "value"},
        )
        assert event.text == "Hello world"
        assert event.actor_handle == "test.bsky.social"
        assert event.like_count == 42
        assert event.raw_payload["key"] == "value"

    def test_media_urls(self):
        event = RawEvent(
            platform="reddit",
            collection_mode="query",
            media_urls=["https://example.com/img.jpg", "https://example.com/img2.png"],
        )
        assert len(event.media_urls) == 2

    def test_thread_context(self):
        event = RawEvent(
            platform="x",
            collection_mode="query",
            parent_native_id="123",
            thread_root_native_id="100",
        )
        assert event.parent_native_id == "123"
        assert event.thread_root_native_id == "100"
