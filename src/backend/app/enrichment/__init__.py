"""Multistage enrichment pipeline.

For every content item:
1. Language detection
2. Dedup / near-dup
3. OCR / ASR / transcript extraction (Phase 2)
4. NER + custom entity linking
5. URL/domain extraction
6. Geocoding where justified (Phase 2)
7. Topic + claim extraction
8. Sentiment/emotion only as weak signals
9. Embedding generation
10. Safety / risk / priority classification
"""
