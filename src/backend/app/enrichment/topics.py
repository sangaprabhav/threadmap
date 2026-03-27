"""Topic and claim extraction — keyword-based for MVP, upgradeable to LLM-based."""

import re
from collections import Counter

# Stop words for topic extraction
STOP_WORDS = frozenset({
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for",
    "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his",
    "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my",
    "one", "all", "would", "there", "their", "what", "so", "up", "out", "if",
    "about", "who", "get", "which", "go", "me", "when", "make", "can", "like",
    "time", "no", "just", "him", "know", "take", "people", "into", "year",
    "your", "good", "some", "could", "them", "see", "other", "than", "then",
    "now", "look", "only", "come", "its", "over", "think", "also", "back",
    "after", "use", "two", "how", "our", "work", "first", "well", "way", "even",
    "new", "want", "because", "any", "these", "give", "day", "most", "us",
    "is", "are", "was", "were", "been", "has", "had", "did", "does",
    "http", "https", "www", "com", "rt",
})


def extract_topics(text: str, max_topics: int = 5) -> list[str]:
    """Extract key topics from text using TF-based keyword extraction.

    MVP approach: normalized word frequency with stop word removal.
    Phase 2: Replace with LLM-based topic/claim extraction.
    """
    if not text or len(text.strip()) < 10:
        return []

    # Tokenize and normalize
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    if not words:
        return []

    # Extract bigrams for more meaningful topics
    bigrams = []
    for i in range(len(words) - 1):
        bigram = f"{words[i]}_{words[i+1]}"
        bigrams.append(bigram)

    # Count frequencies
    word_counts = Counter(words)
    bigram_counts = Counter(bigrams)

    # Combine top unigrams and bigrams
    topics = []
    for word, _ in word_counts.most_common(max_topics):
        topics.append(word)
    for bigram, count in bigram_counts.most_common(3):
        if count > 1:
            topics.append(bigram.replace("_", " "))

    return topics[:max_topics]


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text."""
    return list(set(re.findall(r"#(\w+)", text)))
