from pydantic import BaseModel, Field


class SendingKafkaMessage(BaseModel):
    """
    Requesting model for sending message to Kafka topic

    :param str message: The message for sending to the Kafka topic
    :param str topic: The Kafka topic to which the message will be sent
    """

    message: str = Field(
        default=..., description="The message sending to the Kafka topic"
    )
    topic: str = Field(
        default=..., description="The Kafka topic to which the message will be sent"
    )


class CreateTopicRequest(BaseModel):
    """
    Requesting model for creating new Kafka topic

    :param str topic_name: The name of the topic for creation
    :param int num_partitions: The topic number of partitions
    :param int replication_factor: The topic replication factor
    """

    topic_name: str = Field(..., description="The name of the topic to create")
    num_partitions: int = Field(
        default=1, ge=1, description="The topic number of partitions"
    )
    replication_factor: int = Field(
        default=1, ge=1, description="The topic replication factor"
    )
