# pylint: skip-file
import os
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from dotenv import load_dotenv
from fastapi import status
from httpx import AsyncClient, ConnectError, Response
from sqlalchemy.ext.asyncio import create_async_engine

from app.database.models import Base

from .data_generating_testing import (
    generate_random_keycloak_token,
    generate_test_credentials,
)

load_dotenv()

BACKEND_PORT = os.getenv("BACKEND_PORT")
DATABASE_URL = os.getenv("DATABASE_URL")
REACT_APP_BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL")
REACT_APP_DOMAIN_NAME = os.getenv("REACT_APP_DOMAIN_NAME")

USER, PASSWORD = generate_test_credentials()
ACCESS_TOKEN = generate_random_keycloak_token()
REFRESH_TOKEN = generate_random_keycloak_token()
BASE_URL = f"{REACT_APP_BACKEND_URL}{REACT_APP_DOMAIN_NAME}"
TOKEN_URL = f"{BASE_URL}/api/v1/auth"


class MockKeycloakOpenID:
    """
    A mock class for testing Keycloak OpenID authentication.

    This class provides a mock implementation of the Keycloak OpenID
    client for use in asynchronous tests. It allows for the simulation
    of authentication flows without requiring a real Keycloak server.

    Attributes:
        base_url (str): The base URL for the mock Keycloak server.
    """

    def __init__(self, base_url: str):
        """
        Initializes the MockKeycloakOpenID with a base URL.

        Args:
            base_url (str): The base URL of the Keycloak server.
        """
        self.base_url = base_url

    @classmethod
    async def fetch_token(cls, username: str, password: str) -> Response:
        """
        Mocks the token response for user authentication.

        This method simulates a successful token response when valid
        credentials are provided.

        :param str username: The username for authentication.
        :param str password: The password for authentication.
        :return: A mocked Response object containing the access token.
        """
        if username == USER and password == PASSWORD:
            return Response(
                status_code=status.HTTP_200_OK,
                json={
                    "access_token": ACCESS_TOKEN,
                    "refresh_token": REFRESH_TOKEN,
                    "token_type": "bearer",
                },
            )
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            json={
                "error": "invalid_credentials",
                "access_token": "",
                "refresh_token": "",
            },
        )

    @classmethod
    async def refresh_token(
        cls,
        token: str,
    ) -> Response:
        """
        Mocks the token response for user authentication.

        This method simulates a successful token response when valid
        credentials are provided.

        :param str username: The username for authentication.
        :param str password: The password for authentication.
        :return: A mocked Response object containing the access token.
        """
        if token == ACCESS_TOKEN:
            return Response(
                status_code=status.HTTP_200_OK,
                json={
                    "access_token": ACCESS_TOKEN,
                    "refresh_token": REFRESH_TOKEN,
                    "token_type": "bearer",
                },
            )
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED, json={"error": "token"}
        )

    @classmethod
    def create_event(cls, token: str):
        """
        Simulates events creation

        :param str token: The access token for user information retrieval.

        :returns dict: A dictionary containing mock user information.
        :raises Exception: If the token is invalid.
        """
        if token == ACCESS_TOKEN:
            return Response(
                status_code=status.HTTP_200_OK,
                json={
                    "name": "string",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "client_info": "admin-cli",
                },
            )
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            json={"error": "invalid_credentials"},
        )


@pytest.fixture(scope="module")
async def setup_database():
    """
    Fixture for setting up and shutting down database

    This fixture creates database connection and initializes database
    schema before the tests in the module run. It also ensures that the
    database schema is dropped after the tests are completed
    """
    engine = create_async_engine(
        url=DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client_mock_keycloak():
    """
    Fixture that provides AsyncClient for testing with mock Keycloak container

    This fixture initializes AsyncClient before the test and ensures
    that it is properly finished after the test is completed

    :return: The instance of AsyncClient configured for testing
    """
    # Base URL for the mock Keycloak container
    base_url = BASE_URL
    # Create an instance of the mock Keycloak client
    mock_keycloak = MockKeycloakOpenID(base_url)
    # Create an AsyncClient for making requests
    async with AsyncClient(base_url=base_url) as client:
        # Patch the methods of the mock Keycloak client
        with (
            patch.object(
                mock_keycloak, "fetch_token", new_callable=AsyncMock
            ) as mock_fetch_token,
            patch.object(
                mock_keycloak, "refresh_token", new_callable=AsyncMock
            ) as mock_refresh_token,
            patch.object(
                mock_keycloak, "create_event", new_callable=AsyncMock
            ) as mock_create_event,
        ):
            mock_fetch_token.config = "mocked_config"
            # Set return values for the mocked methods
            mock_fetch_token.return_value = {
                "access_token": ACCESS_TOKEN,
                "refresh_token": REFRESH_TOKEN,
                "expires_in": 60,
                "refresh_expires_in": 1800,
                "not_before_policy": "0",
            }
            mock_refresh_token.config = "mocked_config"
            mock_refresh_token.return_value = {
                "access_token": generate_random_keycloak_token(),
                "refresh_token": generate_random_keycloak_token(),
                "expires_in": 60,
                "refresh_expires_in": 1800,
                "not_before_policy": "0",
            }
            mock_create_event.config = "mocked_config"
            mock_create_event.return_value = {
                "name": "string",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "client_info": "admin-cli",
            }

            yield client, mock_keycloak


async def is_responsive(url):
    """
    Check if the input URL is responsive

    :param str url: The URL for responsiveness check

    :return bool: True if the response status code is successful, False otherwise
    """
    try:
        async with AsyncClient() as client:
            response = await client.get(url=url)
            if response.status_code == status.HTTP_200_OK:
                return True
    except ConnectError:
        return False


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """
    Fixture that provides the path to the Docker Compose file

    :param pytestconfig pytestconfig: The pytest configuration object

    :return Path: The path to the Docker Compose file
    """
    return Path(pytestconfig.rootdir).parent / "compose.yaml"


@pytest.fixture(scope="function")
async def backend_container_runner(docker_ip, docker_services):
    """
    Fixture that ensures the backend container is up and responsive

    This fixture waits until the HTTP service is responsive and yields
    AsyncClient instance for making requests to the service

    :param str docker_ip: The IP address of the Docker service
    :param docker_services docker_services: The Docker services fixture

    :yield AsyncClient: An AsyncClient instance for the backend service
    """
    try:
        BACKEND_PORT_VALUE = int(BACKEND_PORT)
    except ValueError as excp:
        raise ValueError("Converting value to integer error") from excp

    port = docker_services.port_for("backend", BACKEND_PORT_VALUE)
    url = f"http://{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=210, pause=0.1, check=lambda: is_responsive(url=url)
    )
    async with AsyncClient(base_url=url) as client:
        time.sleep(5)
        yield client


@pytest.fixture
def current_access_token():
    """
    Fixture that provides access token for Keycloak container

    :return str ACCESS_TOKEN: Access token
    """
    return ACCESS_TOKEN
