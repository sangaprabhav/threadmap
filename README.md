# ThreadMap — Event-Native Intelligence Operating System

A real-time, multimodal, provenance-backed intelligence graph with analyst-in-the-loop automation.

## Architecture

ThreadMap is built on five non-negotiable properties:

1. **Event-native** — ingests streams in real time, not just periodic searches
2. **Provenance-first** — every conclusion traces back to exact posts, media, timestamps, and transformations
3. **Cross-source** — links identities, narratives, domains, channels, and media across platforms
4. **Multimodal** — text, image, video, OCR, speech, metadata, and graph signals all feed the same model layer
5. **Analyst-supervised** — AI drafts findings, but humans control escalation, labeling, and confidence

## Collection Fabric

Source-adaptive connectors with four lanes:

| Lane | Sources | Mode |
|------|---------|------|
| Streaming | Bluesky Jetstream, X stream | Real-time WebSocket/SSE |
| Query/Backfill | Reddit, YouTube, X search | Paginated API polling |
| Web/News/RSS | RSS feeds, news sites, blogs | Feed parsing |
| Analyst Ingest | URLs, text, CSV, JSON, screenshots | Manual submission |

## Canonical Intelligence Schema

| Object | Description |
|--------|-------------|
| Source | Platform, URL, collector, auth mode, legal basis |
| Actor | Account, channel, domain owner, org, person |
| Content | Post, comment, thread, article, video, transcript |
| MediaAsset | Image, frame, audio, OCR text, perceptual hashes |
| Claim | Extracted assertion with canonical form |
| Entity | Person, org, product, location, event |
| NarrativeCluster | Semantically related claims/content |
| Alert | Machine-generated candidate signal |
| Case | Analyst-owned investigation object |
| Edge | Scored relationship between any two objects |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API | FastAPI (Python) |
| Collectors | Python (Go/Rust planned) |
| Enrichment | spaCy, sentence-transformers, langdetect |
| Stream Bus | Redpanda (Kafka-compatible) |
| Transactional DB | PostgreSQL |
| Search | OpenSearch |
| Analytics | ClickHouse |
| Object Storage | MinIO (S3-compatible) |
| Frontend | Next.js + React + Tailwind CSS |

## Quick Start

### 1. Start Infrastructure

```bash
cd infrastructure
docker compose up -d
```

### 2. Backend

```bash
cd src/backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m spacy download en_core_web_sm

# Run migrations
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

# Start API server
uvicorn app.main:app --reload
```

### 3. Frontend

```bash
cd src/frontend
npm install
npm run dev
```

### 4. Run a Collector

```bash
# Bluesky real-time firehose
python scripts/run_collector.py bluesky

# Reddit search
python scripts/run_collector.py reddit --query "topic"

# YouTube search
python scripts/run_collector.py youtube --query "topic"

# RSS feeds
python scripts/run_collector.py rss --feeds "https://feed1.xml,https://feed2.xml"
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | System health and collector status |
| `GET /api/v1/content/stream` | Live event stream |
| `POST /api/v1/content/search` | Search with filters |
| `GET /api/v1/alerts` | Alert inbox |
| `POST /api/v1/alerts/{id}/triage` | Analyst triage action |
| `GET /api/v1/cases` | Investigation cases |
| `POST /api/v1/cases` | Create investigation |
| `GET /api/v1/watchlists` | Monitoring targets |
| `POST /api/v1/ingest/url` | Submit URL evidence |
| `POST /api/v1/ingest/text` | Submit text evidence |
| `GET /api/v1/briefs/daily` | Daily intelligence brief |

## Enrichment Pipeline

Every content item passes through:

1. Language detection
2. Dedup / near-duplicate (SimHash)
3. Named entity recognition (spaCy)
4. URL/domain extraction
5. Topic extraction
6. Embedding generation (sentence-transformers)
7. Risk classification
8. Watchlist matching

## Provenance

Every intelligence artifact tracks:
- Original source ID / URL
- Collection timestamp (when we fetched it)
- Observed timestamp (when source says it happened)
- Transformation chain (every enrichment step)
- Model version
- Confidence score and rationale
- Evidence attachments (S3 keys)

Without this, the system would be an LLM rumor machine.

## Phase Roadmap

### Phase 1: Elite MVP (current)
- Bluesky, X, Reddit, YouTube, RSS, manual ingest
- Watchlists, alerts, daily briefs, case management
- Full enrichment pipeline with provenance

### Phase 2: Intelligence-Grade
- Coordination detection
- Narrative propagation graphs
- Multimodal matching (image/video perceptual hashing)
- Cross-source identity resolution
- Analyst feedback training loop

### Phase 3: Enterprise-Grade
- Multi-tenant architecture
- Custom ontologies
- Role-based review queues
- Policy engine, export controls, legal holds
- Connector SDK

## License

Apache 2.0
