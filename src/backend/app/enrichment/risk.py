"""Risk classification — safety/risk/priority scoring.

MVP: keyword and pattern-based classification.
Phase 2: Fine-tuned classifier or LLM-based assessment.
"""

import re

# Risk signal patterns (not sentiment — structure, velocity, novelty matter more)
RISK_PATTERNS = {
    "threat": {
        "patterns": [
            r"\b(threat|threaten|kill|bomb|attack|weapon|explosive|shoot)\b",
            r"\b(destroy|eliminate|assassinate|execute)\b",
        ],
        "weight": 0.9,
    },
    "coordination": {
        "patterns": [
            r"\b(join\s+us|spread\s+the\s+word|everyone\s+share|mass\s+report)\b",
            r"\b(operation|raid|target|brigade|swarm)\b",
        ],
        "weight": 0.6,
    },
    "disinfo_markers": {
        "patterns": [
            r"\b(wake\s+up|they\s+don't\s+want\s+you\s+to\s+know|mainstream\s+media\s+won't)\b",
            r"\b(exposed|truth\s+about|cover[\s-]?up|false[\s-]?flag)\b",
        ],
        "weight": 0.4,
    },
    "urgency": {
        "patterns": [
            r"\b(breaking|urgent|emergency|happening\s+now|developing)\b",
            r"\b(alert|warning|just\s+in|confirmed)\b",
        ],
        "weight": 0.3,
    },
    "manipulation": {
        "patterns": [
            r"\b(fake\s+account|bot|shill|astroturf|sockpuppet|paid\s+troll)\b",
        ],
        "weight": 0.5,
    },
}


def classify_risk(text: str, entities: list[dict] | None = None) -> dict:
    """Classify risk level of content.

    Returns {"score": float, "labels": [str], "signals": [dict]}
    Score is 0.0 (benign) to 1.0 (critical).
    """
    if not text:
        return {"score": 0.0, "labels": [], "signals": []}

    text_lower = text.lower()
    signals = []
    total_weight = 0.0

    for category, config in RISK_PATTERNS.items():
        for pattern in config["patterns"]:
            matches = re.findall(pattern, text_lower)
            if matches:
                signals.append({
                    "category": category,
                    "pattern": pattern,
                    "matches": matches[:5],
                    "weight": config["weight"],
                })
                total_weight += config["weight"]

    # Normalize score to 0-1 range
    score = min(total_weight / 2.0, 1.0)

    # Determine labels
    labels = list(set(s["category"] for s in signals))

    # Boost score if high-value entities are mentioned
    if entities:
        entity_types = {e.get("label") for e in entities}
        if "PERSON" in entity_types and score > 0.3:
            score = min(score + 0.1, 1.0)
        if "GPE" in entity_types and score > 0.3:
            score = min(score + 0.05, 1.0)

    return {
        "score": round(score, 3),
        "labels": labels,
        "signals": signals,
    }
