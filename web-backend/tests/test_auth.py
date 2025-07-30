from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient, Response

from .conftest import ACCESS_TOKEN, PASSWORD, USER, MockKeycloakOpenID
from .data_generating_testing import generate_test_credentials

NOT_TESTABLE_USER, NOT_TESTABLE_PASSWORD = generate_test_credentials()


# Example test case using the fixture
@pytest.mark.anyio
async def test_sucess_keycloak_auth(
    client_mock_keycloak: tuple[AsyncClient, MockKeycloakOpenID],
):
    """
    Test to create a mock Keycloak client and an AsyncClient.

    Returns:
        Tuple[AsyncClient, MockKeycloakOpenID]: A tuple containing the
        AsyncClient and the mock Keycloak client.
    """
    async_client, mock_keycloak = client_mock_keycloak

    # Use the mock Keycloak client to get a token
    token_response = await mock_keycloak.fetch_token(USER, PASSWORD)
    assert token_response["access_token"] == ACCESS_TOKEN

    with patch.object(async_client, "post", new_callable=AsyncMock) as mock_get:
        # Substitute the response data and status code
        mock_get.return_value = Response(
            status_code=status.HTTP_200_OK, json={"message": "success"}
        )

        # Make a request to the mocked endpoint
        response = await async_client.post("/api/v1/auth/token")

        # Assert the status code
        assert response.status_code == status.HTTP_200_OK

        # Assert the response data
        assert response.json() == {"message": "success"}


@pytest.mark.anyio
async def test_unsucess_keycloak_auth(
    client_mock_keycloak: tuple[AsyncClient, MockKeycloakOpenID],
):
    """Test to create a mock Keycloak client and an AsyncClient.

    Returns:
        Tuple[AsyncClient, MockKeycloakOpenID]: A tuple containing the
        AsyncClient and the mock Keycloak client.
    """
    async_client, mock_keycloak = client_mock_keycloak

    # Use the mock Keycloak client to get a token
    token_response = await mock_keycloak.fetch_token(
        NOT_TESTABLE_USER, NOT_TESTABLE_PASSWORD
    )
    assert token_response["access_token"] == ACCESS_TOKEN

    with patch.object(async_client, "post", new_callable=AsyncMock) as mock_get:
        # Substitute the response data and status code

        # Make a request to the mocked endpoint
        mock_get.return_value = Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            json={"message": "Unsucessful auth"},
        )
        response = await async_client.post("/api/v1/auth/token")
        # Assert the status code
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
