# pylint: skip-file
import os
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from dotenv import load_dotenv
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import create_async_engine

from app.database.models import Base

from .data_generating_testing import (
    generate_random_keycloak_token,
    generate_test_credentials,
)

load_dotenv()

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
        return Response(status_code=status.HTTP_401_UNAUTHORIZED, json={"error": "token"})

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
                    "client_info": "admin-cli"
                }
            )
        return Response(status_code=status.HTTP_401_UNAUTHORIZED, json={"error": "invalid_credentials"})


@pytest.fixture(scope="module")
async def setup_database():
    """
    Database connection async fixture
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
async def test_client_mock_keycloak():
    """
     Fixture that provides an AsyncClient for testing with a mock Keycloak server.

     This fixture initializes an AsyncClient before the test and ensures
     that it is properly closed after the test is completed.

    :return: An instance of AsyncClient configured for testing.
    """
    # Base URL for the mock Keycloak server
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
                "client_info": "admin-cli"
            }


            yield client, mock_keycloak


@pytest.fixture
def current_access_token():
    """
     Fixture that provides an AsyncClient for testing with a mock Keycloak server.

     This fixture initializes an AsyncClient before the test and ensures
     that it is properly closed after the test is completed.

    :return: An instance of AsyncClient configured for testing.
    """
    return ACCESS_TOKEN
