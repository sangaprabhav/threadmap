"""Kafka/Redpanda event producer — the event backbone.

All raw collector events are published to the stream bus for
downstream enrichment, indexing, and alerting.
"""

import orjson
import structlog
from aiokafka import AIOKafkaProducer

from app.core.config import settings

logger = structlog.get_logger()

_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: orjson.dumps(v),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            compression_type="lz4",
        )
        await _producer.start()
        logger.info("kafka.producer.started")
    return _producer


async def publish_raw_event(event_data: dict, key: str | None = None) -> None:
    """Publish a raw collector event to the raw events topic."""
    producer = await get_producer()
    await producer.send_and_wait(
        settings.kafka_topic_raw_events,
        value=event_data,
        key=key or event_data.get("event_id"),
    )


async def publish_enriched_event(event_data: dict, key: str | None = None) -> None:
    """Publish an enriched event after pipeline processing."""
    producer = await get_producer()
    await producer.send_and_wait(
        settings.kafka_topic_enriched,
        value=event_data,
        key=key or event_data.get("event_id"),
    )


async def publish_alert(alert_data: dict, key: str | None = None) -> None:
    """Publish an alert event."""
    producer = await get_producer()
    await producer.send_and_wait(
        settings.kafka_topic_alerts,
        value=alert_data,
        key=key,
    )


async def shutdown_producer() -> None:
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
        logger.info("kafka.producer.stopped")
