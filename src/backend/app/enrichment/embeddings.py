"""Embedding generation — dense vectors for semantic search and clustering."""

import structlog
from functools import lru_cache

logger = structlog.get_logger()

_model = None


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            from app.core.config import settings
            _model = SentenceTransformer(settings.embedding_model)
            logger.info("embeddings.model_loaded", model=settings.embedding_model)
        except Exception as e:
            logger.warning("embeddings.model_load_failed", error=str(e))
            return None
    return _model


async def generate_embedding(text: str) -> list[float] | None:
    """Generate a dense embedding vector for the given text.

    Uses sentence-transformers for MVP. Returns a list of floats.
    """
    if not text or len(text.strip()) < 5:
        return None

    model = _get_model()
    if model is None:
        return None

    try:
        # Truncate to model's max sequence length
        embedding = model.encode(text[:512], show_progress_bar=False)
        return embedding.tolist()
    except Exception as e:
        logger.error("embeddings.generation_error", error=str(e))
        return None


async def generate_embeddings_batch(texts: list[str]) -> list[list[float] | None]:
    """Batch embedding generation for efficiency."""
    model = _get_model()
    if model is None:
        return [None] * len(texts)

    try:
        valid_texts = [t[:512] if t and len(t.strip()) >= 5 else "" for t in texts]
        embeddings = model.encode(valid_texts, show_progress_bar=False, batch_size=32)
        return [
            emb.tolist() if text else None
            for emb, text in zip(embeddings, valid_texts)
        ]
    except Exception as e:
        logger.error("embeddings.batch_error", error=str(e))
        return [None] * len(texts)
