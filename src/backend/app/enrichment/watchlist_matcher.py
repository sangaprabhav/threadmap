"""Watchlist matching — check enriched events against active watchlists."""

import re
import structlog

logger = structlog.get_logger()

# In-memory watchlist cache (refreshed periodically from DB)
_watchlist_cache: list[dict] = []


def update_watchlist_cache(entries: list[dict]) -> None:
    """Update the in-memory watchlist cache."""
    global _watchlist_cache
    _watchlist_cache = entries
    logger.info("watchlist.cache_updated", count=len(entries))


async def match_watchlists(enriched_event: dict) -> list[dict]:
    """Check an enriched event against all active watchlist entries.

    Returns list of matched entries with match details.
    """
    if not _watchlist_cache:
        return []

    matches = []
    text = (enriched_event.get("text") or "").lower()
    title = (enriched_event.get("title") or "").lower()
    combined = f"{title} {text}"
    actor_handle = (enriched_event.get("actor_handle") or "").lower()
    urls = enriched_event.get("extracted_urls", [])
    domains = enriched_event.get("extracted_domains", [])

    for entry in _watchlist_cache:
        value = entry.get("value", "").lower()
        entry_type = entry.get("entry_type", "keyword")
        matched = False
        match_context = ""

        if entry_type == "keyword":
            if value in combined:
                matched = True
                match_context = f"keyword '{value}' found in text"
        elif entry_type == "handle":
            if value == actor_handle or value in combined:
                matched = True
                match_context = f"handle '{value}' matched"
        elif entry_type == "domain":
            if value in domains or any(value in u for u in urls):
                matched = True
                match_context = f"domain '{value}' found"
        elif entry_type == "hashtag":
            hashtags = enriched_event.get("hashtags", [])
            if value.lstrip("#") in [h.lower() for h in hashtags]:
                matched = True
                match_context = f"hashtag '{value}' matched"
        elif entry_type == "regex":
            try:
                if re.search(entry.get("value", ""), combined, re.IGNORECASE):
                    matched = True
                    match_context = f"regex pattern matched"
            except re.error:
                pass

        if matched:
            matches.append({
                "watchlist_id": entry.get("watchlist_id"),
                "entry_id": entry.get("id"),
                "value": entry.get("value"),
                "entry_type": entry_type,
                "match_context": match_context,
            })

    return matches
