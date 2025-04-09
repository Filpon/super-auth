import os
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient

KAFKA_HOSTNAME = os.getenv("KAFKA_HOSTNAME")
KAFKA_PORT = os.getenv("KAFKA_PORT")

async def start_kafka_producer() -> AIOKafkaProducer:
    """
    Create a Kafka producer with the provided access token.

    :param access_token: The access token for authentication with Kafka.
    :return KafkaProducer: KafkaProducer instance.
    """
    producer = AIOKafkaProducer(bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}")
    await producer.start()
    return producer

@asynccontextmanager
async def start_admin_client() -> AIOKafkaAdminClient:
    """
    Create a Kafka producer with the provided access token.

    :param access_token: The access token for authentication with Kafka.
    :return AIOKafkaAdminClient: AIOKafkaAdminClient instance.
    """
    admin_client = AIOKafkaAdminClient(bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}")
    try:
        yield admin_client
    finally:
        await admin_client.close()
