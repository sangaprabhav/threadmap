"""Deduplication / near-duplicate detection.

Uses SimHash for near-duplicate detection. Two texts with a small
Hamming distance between their SimHash values are likely near-duplicates.
"""

import hashlib
import re


def compute_dedup_hash(text: str) -> str:
    """Compute a normalized hash for deduplication.

    Normalizes text (lowercase, strip URLs, collapse whitespace) then SHA-256.
    For near-dup, use SimHash comparison with the raw shingles.
    """
    normalized = _normalize(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]


def compute_simhash(text: str, shingle_size: int = 3) -> int:
    """Compute a 64-bit SimHash for near-duplicate detection."""
    normalized = _normalize(text)
    tokens = normalized.split()
    if len(tokens) < shingle_size:
        shingles = [normalized]
    else:
        shingles = [
            " ".join(tokens[i : i + shingle_size])
            for i in range(len(tokens) - shingle_size + 1)
        ]

    v = [0] * 64
    for shingle in shingles:
        h = int(hashlib.md5(shingle.encode("utf-8")).hexdigest(), 16)
        for i in range(64):
            if h & (1 << i):
                v[i] += 1
            else:
                v[i] -= 1

    fingerprint = 0
    for i in range(64):
        if v[i] > 0:
            fingerprint |= 1 << i
    return fingerprint


def hamming_distance(a: int, b: int) -> int:
    """Compute Hamming distance between two SimHash values."""
    return bin(a ^ b).count("1")


def is_near_duplicate(hash_a: int, hash_b: int, threshold: int = 6) -> bool:
    """Two items are near-duplicates if Hamming distance <= threshold."""
    return hamming_distance(hash_a, hash_b) <= threshold


def _normalize(text: str) -> str:
    """Normalize text for dedup comparison."""
    text = text.lower()
    text = re.sub(r"https?://\S+", "", text)  # Strip URLs
    text = re.sub(r"@\w+", "", text)  # Strip mentions
    text = re.sub(r"#\w+", "", text)  # Strip hashtags
    text = re.sub(r"\s+", " ", text).strip()  # Collapse whitespace
    return text
