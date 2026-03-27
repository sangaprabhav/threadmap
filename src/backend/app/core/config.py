"""ThreadMap configuration — all settings from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "TM_", "env_file": ".env", "extra": "ignore"}

    # App
    app_name: str = "ThreadMap"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    api_prefix: str = "/api/v1"

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "threadmap"
    postgres_password: str = "threadmap"
    postgres_db: str = "threadmap"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Kafka / Redpanda
    kafka_bootstrap_servers: str = "localhost:19092"
    kafka_topic_raw_events: str = "threadmap.raw"
    kafka_topic_enriched: str = "threadmap.enriched"
    kafka_topic_alerts: str = "threadmap.alerts"
    kafka_consumer_group: str = "threadmap-workers"

    # OpenSearch
    opensearch_host: str = "localhost"
    opensearch_port: int = 9200
    opensearch_index_content: str = "threadmap-content"
    opensearch_index_entities: str = "threadmap-entities"

    # ClickHouse
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_db: str = "threadmap"

    # S3 / MinIO
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "threadmap"
    s3_secret_key: str = "threadmap-secret"
    s3_bucket_evidence: str = "evidence"
    s3_bucket_media: str = "media"

    # Collector credentials
    bluesky_firehose_url: str = "wss://jetstream2.us-east.bsky.network/subscribe"
    x_bearer_token: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    youtube_api_key: str = ""

    # Enrichment
    spacy_model: str = "en_core_web_sm"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Auth
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
