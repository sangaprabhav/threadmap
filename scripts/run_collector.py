#!/usr/bin/env python3
"""Run a collector and publish events to the stream bus.

Usage:
    python scripts/run_collector.py bluesky
    python scripts/run_collector.py reddit --query "topic" --subreddit "news"
    python scripts/run_collector.py youtube --query "topic"
    python scripts/run_collector.py rss --feeds "https://feed1.xml,https://feed2.xml"
"""

import argparse
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "backend"))

from app.collectors.base import RawEvent


async def run_bluesky():
    from app.collectors.bluesky.jetstream import BlueskyJetstreamCollector

    collector = BlueskyJetstreamCollector()
    print("Starting Bluesky Jetstream collector...")
    async for event in collector.collect():
        print(f"[bluesky] {event.actor_handle}: {(event.text or '')[:100]}")


async def run_x(query: str):
    from app.collectors.x.search import XSearchCollector

    collector = XSearchCollector()
    print(f"Searching X for: {query}")
    async for event in collector.search(query):
        print(f"[x] @{event.actor_handle}: {(event.text or '')[:100]}")


async def run_reddit(query: str, subreddit: str | None = None):
    from app.collectors.reddit.collector import RedditCollector

    collector = RedditCollector()
    print(f"Searching Reddit for: {query}")
    async for event in collector.search(query, subreddit=subreddit):
        print(f"[reddit] u/{event.actor_handle}: {event.title or (event.text or '')[:100]}")


async def run_youtube(query: str):
    from app.collectors.youtube.collector import YouTubeCollector

    collector = YouTubeCollector()
    print(f"Searching YouTube for: {query}")
    async for event in collector.search(query):
        print(f"[youtube] {event.actor_handle}: {event.title}")


async def run_rss(feeds: list[str]):
    from app.collectors.rss.collector import RSSCollector

    collector = RSSCollector()
    print(f"Fetching {len(feeds)} RSS feeds...")
    async for event in collector.collect(feed_urls=feeds):
        print(f"[rss] {event.actor_handle}: {event.title}")


def main():
    parser = argparse.ArgumentParser(description="Run a ThreadMap collector")
    parser.add_argument("collector", choices=["bluesky", "x", "reddit", "youtube", "rss"])
    parser.add_argument("--query", "-q", default="", help="Search query")
    parser.add_argument("--subreddit", "-s", default=None, help="Reddit subreddit")
    parser.add_argument("--feeds", "-f", default="", help="Comma-separated RSS feed URLs")

    args = parser.parse_args()

    if args.collector == "bluesky":
        asyncio.run(run_bluesky())
    elif args.collector == "x":
        asyncio.run(run_x(args.query))
    elif args.collector == "reddit":
        asyncio.run(run_reddit(args.query, args.subreddit))
    elif args.collector == "youtube":
        asyncio.run(run_youtube(args.query))
    elif args.collector == "rss":
        feeds = [f.strip() for f in args.feeds.split(",") if f.strip()]
        asyncio.run(run_rss(feeds))


if __name__ == "__main__":
    main()
