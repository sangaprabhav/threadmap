"""Provenance tracker — records the full lineage of every intelligence artifact.

Non-negotiable: every analytic conclusion must be reproducible from:
  - original source ID / URL
  - collection timestamp
  - observed timestamp
  - normalized timestamp
  - transformation chain
  - model version
  - prompt/template version
  - confidence and rationale
  - evidence attachments
"""

from datetime import datetime, timezone
from typing import Any


class ProvenanceRecord:
    """Immutable provenance record for an intelligence artifact."""

    def __init__(
        self,
        source_url: str | None = None,
        source_native_id: str | None = None,
        platform: str | None = None,
        collected_at: datetime | None = None,
        observed_at: datetime | None = None,
    ):
        self.source_url = source_url
        self.source_native_id = source_native_id
        self.platform = platform
        self.collected_at = collected_at or datetime.now(timezone.utc)
        self.observed_at = observed_at
        self.normalized_at = datetime.now(timezone.utc)
        self.transformation_chain: list[dict[str, Any]] = []
        self.model_version: str | None = None
        self.prompt_version: str | None = None
        self.confidence: float | None = None
        self.confidence_rationale: str | None = None
        self.evidence_keys: list[str] = []

    def add_transformation(
        self,
        step: str,
        version: str | None = None,
        result: Any = None,
        model: str | None = None,
    ) -> "ProvenanceRecord":
        """Record a transformation step in the chain."""
        self.transformation_chain.append({
            "step": step,
            "version": version,
            "model": model,
            "result_summary": str(result)[:200] if result else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if model:
            self.model_version = model
        return self

    def set_confidence(self, score: float, rationale: str) -> "ProvenanceRecord":
        self.confidence = score
        self.confidence_rationale = rationale
        return self

    def add_evidence(self, s3_key: str) -> "ProvenanceRecord":
        self.evidence_keys.append(s3_key)
        return self

    def to_dict(self) -> dict:
        return {
            "source_url": self.source_url,
            "source_native_id": self.source_native_id,
            "platform": self.platform,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "observed_at": self.observed_at.isoformat() if self.observed_at else None,
            "normalized_at": self.normalized_at.isoformat(),
            "transformation_chain": self.transformation_chain,
            "model_version": self.model_version,
            "prompt_version": self.prompt_version,
            "confidence": self.confidence,
            "confidence_rationale": self.confidence_rationale,
            "evidence_keys": self.evidence_keys,
        }
