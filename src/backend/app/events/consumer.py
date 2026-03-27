"""Kafka/Redpanda event consumer — processes raw events through the enrichment pipeline."""

import orjson
import structlog
from aiokafka import AIOKafkaConsumer

from app.core.config import settings

logger = structlog.get_logger()


async def create_consumer(topic: str, group_id: str | None = None) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id or settings.kafka_consumer_group,
        value_deserializer=lambda v: orjson.loads(v),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    await consumer.start()
    logger.info("kafka.consumer.started", topic=topic, group=group_id)
    return consumer


async def consume_raw_events(handler):
    """Consume raw events and pass them through the enrichment handler."""
    consumer = await create_consumer(settings.kafka_topic_raw_events)
    try:
        async for msg in consumer:
            try:
                await handler(msg.value)
            except Exception as e:
                logger.error("kafka.consumer.handler_error", error=str(e), topic=msg.topic)
    finally:
        await consumer.stop()
