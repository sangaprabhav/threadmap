"""Named Entity Recognition — extract persons, orgs, locations, events."""

import structlog

logger = structlog.get_logger()

# Lazy-loaded spaCy model
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("ner.spacy_model_not_found", msg="Run: python -m spacy download en_core_web_sm")
            return None
    return _nlp


def extract_entities(text: str) -> list[dict]:
    """Extract named entities from text using spaCy.

    Returns list of {text, label, start, end} dicts.
    Labels: PERSON, ORG, GPE, LOC, EVENT, PRODUCT, NORP, FAC, DATE, etc.
    """
    if not text or len(text.strip()) < 5:
        return []

    nlp = _get_nlp()
    if nlp is None:
        return _fallback_extract(text)

    # Process with character limit to avoid memory issues
    doc = nlp(text[:10000])

    entities = []
    seen = set()
    for ent in doc.ents:
        key = (ent.text.strip(), ent.label_)
        if key in seen:
            continue
        seen.add(key)
        entities.append({
            "text": ent.text.strip(),
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        })

    return entities


def _fallback_extract(text: str) -> list[dict]:
    """Basic regex-based entity extraction as fallback when spaCy is unavailable."""
    import re
    entities = []

    # Simple patterns for common entity types
    # @mentions as potential person/org references
    for match in re.finditer(r"@(\w+)", text):
        entities.append({
            "text": match.group(0),
            "label": "MENTION",
            "start": match.start(),
            "end": match.end(),
        })

    # Capitalized multi-word sequences (potential proper nouns)
    for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text):
        entities.append({
            "text": match.group(0),
            "label": "PROPER_NOUN",
            "start": match.start(),
            "end": match.end(),
        })

    return entities
