"""Tests for the enrichment pipeline stages."""

import pytest

from app.enrichment.language import detect_language
from app.enrichment.dedup import compute_dedup_hash, compute_simhash, is_near_duplicate, hamming_distance
from app.enrichment.ner import extract_entities, _fallback_extract
from app.enrichment.urls import extract_urls_and_domains
from app.enrichment.topics import extract_topics, extract_hashtags
from app.enrichment.risk import classify_risk


class TestLanguageDetection:
    def test_english(self):
        assert detect_language("This is a test sentence in English") == "en"

    def test_short_text_returns_none(self):
        assert detect_language("hi") is None

    def test_empty_returns_none(self):
        assert detect_language("") is None


class TestDedup:
    def test_identical_texts_same_hash(self):
        h1 = compute_dedup_hash("The quick brown fox jumps over the lazy dog")
        h2 = compute_dedup_hash("The quick brown fox jumps over the lazy dog")
        assert h1 == h2

    def test_different_texts_different_hash(self):
        h1 = compute_dedup_hash("The quick brown fox")
        h2 = compute_dedup_hash("A completely different sentence")
        assert h1 != h2

    def test_simhash_near_duplicates(self):
        h1 = compute_simhash("Breaking news: major event happening in the city center")
        h2 = compute_simhash("Breaking news: major event happening at the city center")
        assert is_near_duplicate(h1, h2)

    def test_simhash_different_texts(self):
        h1 = compute_simhash("Breaking news about politics and economics")
        h2 = compute_simhash("Recipe for chocolate cake with cream frosting")
        assert not is_near_duplicate(h1, h2, threshold=3)


class TestURLExtraction:
    def test_extract_urls(self):
        text = "Check out https://example.com and http://test.org/page for more info"
        result = extract_urls_and_domains(text)
        assert len(result["urls"]) == 2
        assert "example.com" in result["domains"]
        assert "test.org" in result["domains"]

    def test_no_urls(self):
        result = extract_urls_and_domains("No URLs here")
        assert result["urls"] == []
        assert result["domains"] == []

    def test_empty(self):
        result = extract_urls_and_domains("")
        assert result["urls"] == []


class TestTopicExtraction:
    def test_extracts_topics(self):
        text = "The government announced new climate change policy measures affecting energy production and renewable energy investments"
        topics = extract_topics(text)
        assert len(topics) > 0

    def test_short_text_empty(self):
        assert extract_topics("hi") == []

    def test_hashtags(self):
        hashtags = extract_hashtags("Breaking #news about #climate and #politics")
        assert "news" in hashtags
        assert "climate" in hashtags


class TestRiskClassification:
    def test_benign_text(self):
        result = classify_risk("The weather today is quite nice and sunny")
        assert result["score"] < 0.3
        assert len(result["labels"]) == 0

    def test_risk_signals(self):
        result = classify_risk("Breaking alert: urgent threat detected in the area, attack imminent")
        assert result["score"] > 0.3
        assert len(result["labels"]) > 0

    def test_empty_text(self):
        result = classify_risk("")
        assert result["score"] == 0.0


class TestNERFallback:
    def test_fallback_mentions(self):
        entities = _fallback_extract("@user1 said something to @user2")
        mentions = [e for e in entities if e["label"] == "MENTION"]
        assert len(mentions) == 2

    def test_fallback_proper_nouns(self):
        entities = _fallback_extract("John Smith met with Jane Doe at the White House")
        proper = [e for e in entities if e["label"] == "PROPER_NOUN"]
        assert len(proper) > 0
