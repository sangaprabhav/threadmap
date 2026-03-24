"""Language detection stage."""

from langdetect import detect, DetectorFactory

# Ensure reproducible results
DetectorFactory.seed = 0


def detect_language(text: str) -> str | None:
    """Detect the language of the given text. Returns ISO 639-1 code."""
    if not text or len(text.strip()) < 10:
        return None
    try:
        return detect(text)
    except Exception:
        return None
