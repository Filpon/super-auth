import os
from contextlib import asynccontextmanager
from typing import Final

from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import (
    KafkaConnectionError,
    KafkaError,
    KafkaTimeoutError,
    TopicAlreadyExistsError,
)
from dotenv import load_dotenv
from fastapi import HTTPException, status

from app.configs.logging_handler import configure_logging_handler

logger = configure_logging_handler()

load_dotenv()

KAFKA_HOSTNAME: Final[str] = os.getenv("KAFKA_HOSTNAME")
KAFKA_PORT: Final[str] = os.getenv("KAFKA_PORT")


class KafkaAdmin:
    """
    Manage Kafka topics using the Kafka Admin Client

    This class provides methods for creation, deleting and listing Kafka topics,
    as well as to start and stop the Kafka Admin client
    """

    def __init__(self, bootstrap_servers: str):
        """
        Initialize Kafka Admin instance

        :param str bootstrap_servers: Kafka connecting servers
        """
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = None

    async def start(self):
        """
        Start active Kafka admin client instance

        """
        try:
            self.admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers
            )
            await self.admin_client.start()
            logger.info("Admin client Kafka instance was started")
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

    @asynccontextmanager
    async def start_context_manager(self):
        """
        Asynchronous context manager to start the Kafka admin client

        :yield AIOKafkaAdminClient: The Kafka admin client instance
        """
        try:
            await self.start()
            logger.info("Admin client Kafka context manager was started")
            yield self.admin_client
        except KafkaConnectionError as error:
            logger.exception("Unable connect to Kafka server")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Unable connect to Kafka server",
            ) from error
        except Exception as exception:
            logger.exception("Failed to start Kafka, because of %s", exception)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start Kafka, because of {str(exception)}",
            ) from exception
        finally:
            await self.admin_client.close()

    async def stop(self) -> None:
        """
        Stop the Kafka admin client

        """
        try:
            if self.admin_client:
                await self.admin_client.close()
                logger.info("Admin client Kafka instance was finished")
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

    async def create_topic(
        self,
        topic_name: str,
        num_partitions: int = 1,
        replication_factor: int = 1,
    ) -> dict[str, str]:
        """
        Creation new Kafka topic

        :param str topic_name: The name of the topic for creation
        :param int num_partitions: The number of partitions for the topic creation
        :param int replication_factor: The replication factor for the topic creation

        :return dict: Message indicating the success of the topic creation
        """
        try:
            async with self.start_context_manager() as admin_client:
                new_topic = NewTopic(
                    name=topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor,
                )
                await admin_client.create_topics([new_topic])
            logger.info("Topic '%s' was created successfully", topic_name)
            return {"message": f"Topic '{topic_name}' was created successfully"}
        except TopicAlreadyExistsError as error:
            logger.exception("Topic '%s' already exists", topic_name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Topic '{topic_name}' already exists",
            ) from error
        except KafkaError as error:
            logger.exception(
                "Common base broker error for creation topic '%s' - %s",
                topic_name,
                error,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Common base broker error for creation topic '{topic_name}' - {str(error)}",
            ) from error
        except Exception as exception:
            logger.exception(
                "Failed to create topic '%s', because %s", topic_name, exception
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create topic '{topic_name}', because {str(exception)}",
            ) from exception

    async def delete_topic(self, topic_name: str) -> dict[str, str]:
        """
        Deleting Kafka topic

        :param str topic_name: The deleting topic name

        :return dict: Message indicating the success of the topic deleting
        """
        try:
            await self.admin_client.delete_topics([topic_name])
            logger.info("Topic '%s' was deleted successfully", topic_name)
            return {"message": f"Topic '{topic_name}' was deleted successfully"}
        except KafkaError as error:
            logger.exception(
                "Common base broker error for deleting topic '%s' - %s",
                topic_name,
                error,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Common base broker error for deleting topic '{topic_name}' - {str(error)}",
            ) from error
        except Exception as exception:
            logger.exception(
                "Failed to delete topic '%s', because %s", topic_name, exception
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete topic '{topic_name}', because {str(exception)}",
            ) from exception

    async def list_topics(self):
        """
        Listing all Kafka topics

        """
        try:
            topics = await self.admin_client.list_topics()
            for topic in topics:
                logger.info(topic)
        except KafkaError as error:
            logger.exception("Common base broker error for topic listing - %s", error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Common base broker error for topic listing - {str(error)}",
            ) from error
        except Exception as exception:
            logger.exception("Failed to list topics, because %s", exception)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list topics, because {str(exception)}",
            ) from exception


kafka_admin = KafkaAdmin(bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}")
