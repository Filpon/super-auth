import pytest
from fastapi import status


# test_main.py
@pytest.mark.anyio
async def test_health_check(test_client_mock_keycloak):
    """Test the health check endpoint with a valid token."""
    # Mock the Keycloak token decoding
    async_client, _ = test_client_mock_keycloak
    response = await async_client.get("/api")

    assert response.status_code == status.HTTP_200_OK
