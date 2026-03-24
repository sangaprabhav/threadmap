"""Enrichment pipeline orchestrator — runs each stage in sequence on a raw event."""

import structlog
from datetime import datetime, timezone

from app.enrichment.language import detect_language
from app.enrichment.dedup import compute_dedup_hash
from app.enrichment.ner import extract_entities
from app.enrichment.urls import extract_urls_and_domains
from app.enrichment.topics import extract_topics
from app.enrichment.embeddings import generate_embedding
from app.enrichment.risk import classify_risk
from app.enrichment.watchlist_matcher import match_watchlists

logger = structlog.get_logger()


async def enrich_event(raw_event: dict) -> dict:
    """Run the full enrichment pipeline on a raw event.

    Returns the enriched event with all extracted signals added.
    Each enrichment step is recorded in the transformation_chain for provenance.
    """
    enriched = {**raw_event}
    chain = []
    text = raw_event.get("text") or ""
    title = raw_event.get("title") or ""
    combined_text = f"{title} {text}".strip()

    # 1. Language detection
    try:
        lang = detect_language(combined_text)
        enriched["language"] = lang
        chain.append({"step": "language_detection", "result": lang, "ts": _now()})
    except Exception as e:
        logger.warning("enrichment.language.error", error=str(e))

    # 2. Dedup hash
    try:
        dedup_hash = compute_dedup_hash(combined_text)
        enriched["dedup_hash"] = dedup_hash
        chain.append({"step": "dedup_hash", "result": dedup_hash, "ts": _now()})
    except Exception as e:
        logger.warning("enrichment.dedup.error", error=str(e))

    # 3. NER
    try:
        entities = extract_entities(combined_text)
        enriched["extracted_entities"] = entities
        chain.append({"step": "ner", "entity_count": len(entities), "ts": _now()})
    except Exception as e:
        logger.warning("enrichment.ner.error", error=str(e))

    # 4. URL/domain extraction
    try:
        urls_data = extract_urls_and_domains(combined_text)
        enriched["extracted_urls"] = urls_data["urls"]
        enriched["extracted_domains"] = urls_data["domains"]
        chain.append({"step": "url_extraction", "url_count": len(urls_data["urls"]), "ts": _now()})
    except Exception as e:
        logger.warning("enrichment.urls.error", error=str(e))

    # 5. Topic extraction
    try:
        topics = extract_topics(combined_text)
        enriched["topics"] = topics
        chain.append({"step": "topic_extraction", "topic_count": len(topics), "ts": _now()})
    except Exception as e:
        logger.warning("enrichment.topics.error", error=str(e))

    # 6. Embedding generation
    try:
        embedding = await generate_embedding(combined_text)
        enriched["embedding"] = embedding
        chain.append({"step": "embedding", "dim": len(embedding) if embedding else 0, "ts": _now()})
    except Exception as e:
        logger.warning("enrichment.embedding.error", error=str(e))

    # 7. Risk classification
    try:
        risk = classify_risk(combined_text, enriched.get("extracted_entities", []))
        enriched["risk_score"] = risk["score"]
        enriched["risk_labels"] = risk["labels"]
        chain.append({"step": "risk_classification", "score": risk["score"], "ts": _now()})
    except Exception as e:
        logger.warning("enrichment.risk.error", error=str(e))

    # 8. Watchlist matching
    try:
        matches = await match_watchlists(enriched)
        enriched["watchlist_matches"] = matches
        chain.append({"step": "watchlist_match", "match_count": len(matches), "ts": _now()})
    except Exception as e:
        logger.warning("enrichment.watchlist.error", error=str(e))

    enriched["transformation_chain"] = chain
    enriched["enriched_at"] = _now()
    return enriched


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
