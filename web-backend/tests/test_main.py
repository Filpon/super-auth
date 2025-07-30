import pytest
from fastapi import status


# test_main.py
@pytest.mark.anyio
async def test_health_check(backend_container_runner):
    """
    Testing the endpoint avaibility of the backend service

    This test sends GET request to the `/check` endpoint
    of the backend service and asserts that the successful response status code,
    indicating that the service is healthy and responsive

    :param backend_container_runner: Fixture that provides way to
    run the backend container and interact with it during tests
    """
    response = await backend_container_runner.get("/check", timeout=10)
    assert response.status_code == status.HTTP_200_OK
