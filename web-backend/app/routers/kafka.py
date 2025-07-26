import os
from typing import Final

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status

from app.brokers.kafka_admin import KafkaAdmin
from app.brokers.kafka_producer import KafkaProducer
from app.configs.logging import configure_logging_handler
from app.schemas.kafka import CreateTopicRequest, SendingKafkaMessage

load_dotenv()

KAFKA_HOSTNAME: Final[str] = os.getenv("KAFKA_HOSTNAME")
KAFKA_PORT: Final[str] = os.getenv("KAFKA_PORT")

router = APIRouter()
logger = configure_logging_handler()

kafka_admin = KafkaAdmin(bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}")
kafka_producer = KafkaProducer(
    bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}", topic="auth"
)


@router.post("/send")
async def send_message(request: SendingKafkaMessage) -> dict[str, str]:
    """
    Sending message to Kafka topic

    This asynchronous router takes message body content as input
    and sends it to the specified Kafka topic using the Kafka producer

    :param SendingKafkaMessage request: Request content
    :param str message: The message for sending to the Kafka topic

    :return dict: Response indicating the status of the sending message
    """
    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty"
        )
    topic = request.topic
    message = request.message
    await kafka_producer.send_message(topic=topic, message=message)

    return {"message": f"Message sent to Kafka topic {topic}"}


@router.post("/create/topic")
async def create_topic(request: CreateTopicRequest) -> dict[str, str]:
    """
    New Kafka topic creation

    This endpoint allows to create new Kafka topic by providing the topic name,
    number of partitions and replication factor

    :param CreateTopicRequest request: Request content
    :param str topic_name: The name of the topic to create
    :param int num_partitions: The number of partitions for the topic
    :param int replication_factor: The replication factor for the topic

    :return dict: Message indicating the success of the topic creation
    """
    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic message should be provided",
        )
    topic_name = request.topic_name
    num_partitions = request.num_partitions
    replication_factor = request.replication_factor

    await kafka_admin.create_topic(
        topic_name=topic_name,
        num_partitions=num_partitions,
        replication_factor=replication_factor,
    )

    return {"message": f"Topic '{topic_name}' was created"}
