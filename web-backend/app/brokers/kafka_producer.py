import os
from typing import Final

from aiokafka import AIOKafkaProducer
from aiokafka.errors import (
    KafkaConnectionError,
    KafkaError,
    KafkaTimeoutError,
)
from dotenv import load_dotenv
from fastapi import HTTPException, Request, status

from app.configs.logging_handler import configure_logging_handler

logger = configure_logging_handler()

load_dotenv()

KAFKA_HOSTNAME: Final[str] = os.getenv("KAFKA_HOSTNAME")
KAFKA_PORT: Final[str] = os.getenv("KAFKA_PORT")


class KafkaProducer:
    """
    Managing Kafka topics using Kafka Producer

    This class provides methods for start connection Kafka container
    and sending Kafka messages, as well as to start and stop the Kafka producer
    """

    def __init__(self, bootstrap_servers: str, topic: str):
        """
        Initialize the KafkaProducer instance

        :param str bootstrap_servers: Kafka connecting server
        :param str topic: Kafka topic name
        """

        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None

    async def start(self):
        """
        Creation active Kafka producer

        """
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
            )
            await self.producer.start()
            logger.info("Admin client Kafka producer instance was started")
            return self.producer
        except KafkaTimeoutError as error:
            logger.exception("Timeout Kafka connection error")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Timeout Kafka connection error",
            ) from error
        except KafkaConnectionError as error:
            logger.exception("Unable connect to Kafka server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable connect to Kafka server",
            ) from error
        except Exception as exception:
            logger.exception("Failed to start Kafka, because of %s", exception)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start Kafka, because of {str(exception)}",
            ) from exception

    async def send_message(self, topic: str, message: str | bytes) -> None:
        """
        Sending message to Kafka topic

        :param str topic: The Kafka topic for message sending
        :param str | bytes message: The message for sending
        """
        try:
            if isinstance(message, str):
                message = message.encode("utf-8")
            await self.producer.send_and_wait(topic=topic, value=message)
            logger.info("Message was sent to topic '%s'", topic)
        except KafkaConnectionError as error:
            logger.exception("Common base broker error -  %s", error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Common base broker error - {str(error)}",
            ) from error
        except Exception as exception:
            logger.exception("Failed to send message to Kafka, because of %s", exception)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message to Kafka, because of {str(exception)}",
            ) from exception

    async def stop(self):
        """
        Stopping Kafka producer

        """
        try:
            if self.producer:
                await self.producer.stop()
                logger.info("Admin client Kafka producer instance was finished")
            return self.producer()
        except KafkaError as error:
            logger.exception("Common base broker error - %s", error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Common base broker error - {str(error)}",
            ) from error
        except Exception as exception:
            logger.exception("Error - %s", exception)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exception),
            ) from exception


async def get_producer(request: Request):
    """
    Dependency function to retrieve the Kafka producer from the FastAPI application state

    This function accesses the application state to obtain the Kafka producer instance,
    which can be used in route handlers for sending messages to Kafka topics

    :param Request request: The FastAPI request object, which provides access
    to the application state

    :returns: The Kafka producer instance stored in the application state
    """
    logger.info("Application producer instance was used")
    return request.app.state.producer


kafka_producer = KafkaProducer(
    bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}", topic="events"
)
