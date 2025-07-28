# test_main.py
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import Response

from .conftest import PASSWORD, USER


# Example test case using the fixture
@pytest.mark.anyio
async def test_create_event(test_client_mock_keycloak):
    """
    Fixture to create a mock Keycloak client and an AsyncClient.

    Returns:
        Tuple[AsyncClient, MockKeycloakOpenID]: A tuple containing the
        AsyncClient and the mock Keycloak client.
    """
    async_client, mock_keycloak = test_client_mock_keycloak

    # Use the mock Keycloak client to get a token
    token_response = await mock_keycloak.create_event(USER, PASSWORD)
    assert token_response["date"] == datetime.now().strftime("%Y-%m-%d")

    with patch.object(async_client, "post", new_callable=AsyncMock) as mock_post:
        # Substitute the response data and status code
        mock_post.return_value = Response(
            status_code=status.HTTP_200_OK, json={"message": "success"}
        )

        # Make a request to the mocked endpoint
        response = await async_client.post("/api/v1/events")

        assert response.status_code == status.HTTP_200_OK
