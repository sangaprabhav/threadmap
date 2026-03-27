"""Tests for the provenance tracking system."""

from datetime import datetime, timezone

from app.provenance.tracker import ProvenanceRecord


class TestProvenanceRecord:
    def test_basic_record(self):
        record = ProvenanceRecord(
            source_url="https://example.com/post/123",
            platform="test",
            source_native_id="123",
        )
        assert record.source_url == "https://example.com/post/123"
        assert record.platform == "test"
        assert record.collected_at is not None
        assert record.normalized_at is not None

    def test_transformation_chain(self):
        record = ProvenanceRecord(platform="test")
        record.add_transformation("language_detection", version="langdetect-1.0", result="en")
        record.add_transformation("ner", version="spacy-3.7", model="en_core_web_sm")

        assert len(record.transformation_chain) == 2
        assert record.transformation_chain[0]["step"] == "language_detection"
        assert record.model_version == "en_core_web_sm"

    def test_confidence(self):
        record = ProvenanceRecord(platform="test")
        record.set_confidence(0.85, "High entity overlap and temporal correlation")

        assert record.confidence == 0.85
        assert "temporal" in record.confidence_rationale

    def test_evidence_keys(self):
        record = ProvenanceRecord(platform="test")
        record.add_evidence("evidence/2024/01/screenshot.png")
        record.add_evidence("evidence/2024/01/raw_api_response.json")

        assert len(record.evidence_keys) == 2

    def test_to_dict(self):
        record = ProvenanceRecord(
            source_url="https://x.com/user/status/123",
            platform="x",
        )
        record.add_transformation("enrichment", version="v1")
        record.set_confidence(0.9, "Direct match")

        d = record.to_dict()
        assert d["platform"] == "x"
        assert d["confidence"] == 0.9
        assert len(d["transformation_chain"]) == 1
        assert d["source_url"] == "https://x.com/user/status/123"

    def test_chaining(self):
        record = (
            ProvenanceRecord(platform="bluesky")
            .add_transformation("step1")
            .add_transformation("step2")
            .set_confidence(0.7, "Moderate match")
            .add_evidence("key1")
        )
        assert len(record.transformation_chain) == 2
        assert record.confidence == 0.7
        assert len(record.evidence_keys) == 1
