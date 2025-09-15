from datetime import datetime

import pytest
from fastapi import status


@pytest.mark.anyio
async def test_create_topic(backend_container_runner):
    """
    Testing the creation of new Kafka topic.

    The test sends request to create new Kafka topic with a unique name,
    a specified number of partitions, and a replication factor. It asserts that
    the response status code is 200 OK, indicating successful creation

    :param backend_container_runner: Fixture that provides way to
        run the backend container and interact with it during test
    """
    topic = {
        "topic_name": f"test-topic-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}",
        "num_partitions": 1,
        "replication_factor": 1,
    }

    response = await backend_container_runner.post(
        url="/api/v1/kafka/create/topic",
        json=topic,
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_create_existing_topic(backend_container_runner):
    """
    Testing the creation of an existing Kafka topic.

    The test first creates the new Kafka topic and then attempts to create the
    same topic again. It asserts that the response status code for both requests
    is 200 OK, indicating that the topic was created successfully for the first time

    :param backend_container_runner: Fixture that provides way to
        run the backend container and interact with it during tests
    """
    topic = {
        "topic_name": f"test-topic-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}",
        "num_partitions": 1,
        "replication_factor": 1,
    }

    response = await backend_container_runner.post(
        url="/api/v1/kafka/create/topic",
        json=topic,
    )
    assert response.status_code == status.HTTP_200_OK
    response_existing_topic = await backend_container_runner.post(
        url="/api/v1/kafka/create/topic",
        json=topic,
    )
    assert response_existing_topic.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_send_message_topic(backend_container_runner):
    """
    Test sending a message to the Kafka topic

    The test creates the new Kafka topic and then sends a message to the created topic.
    It asserts that the response status code for sending the message is 200 OK,
    indicating successful message delivery

    :param backend_container_runner: Fixture that provides way to
        run the backend container and interact with it during tests
    """
    topic_name = f"test-topic-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
    topic = {"topic_name": topic_name, "num_partitions": 1, "replication_factor": 1}
    response = await backend_container_runner.post(
        url="/api/v1/kafka/create/topic",
        json=topic,
    )
    assert response.status_code == status.HTTP_200_OK

    message = {
        "message": f"Test message {datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}",
        "topic": topic_name,
    }
    response_sending_message = await backend_container_runner.post(
        url="/api/v1/kafka/send",
        json=message,
    )
    assert response_sending_message.status_code == status.HTTP_200_OK
