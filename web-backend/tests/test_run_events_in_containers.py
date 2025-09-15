import json
from datetime import datetime

import pytest
from fastapi import status

from .conftest import KC_REALM_COMMON_CLIENT
from .data_generating_testing import find_event_by_name


@pytest.mark.anyio
async def test_fetch_events(backend_container_runner, admin_user_tokens):
    """
    Testing fetching events from the backend service.

    The test sends GET request to the `/api/v1/events` endpoint
    of the backend service. It asserts that the response status code
    is 200 (OK), indicating that the events were fetched successfully

    :param backend_container_runner: Fixture that provides way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Fixture that provides the access token and refresh token
        for admin user
    """
    response = await backend_container_runner.get(
        url="/api/v1/events",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_create_event(backend_container_runner, admin_user_tokens):
    """
    Test creating an event in the backend service.

    The test sends POST request to the `/api/v1/events/create` endpoint
    of the backend service with generated event name and date. It asserts
    that the response status code is either 200 (OK) or 201 (Created),
    indicating that the event creation was successful. After creation, it
    fetches the list of events and verifies that the created event is present

    :param backend_container_runner: Fixture that provides way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Fixture that provides the access token and refresh token
        for admin user
    """
    event_name = f"Test Event {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    event_data = {
        "name": event_name,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "client_info": KC_REALM_COMMON_CLIENT,
    }
    response_creation = await backend_container_runner.post(
        url="/api/v1/events/create",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"},
        json=event_data,
    )
    assert response_creation.status_code in {
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
    }

    response = await backend_container_runner.get(
        url="/api/v1/events",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    found_event = find_event_by_name(data_string=response.text, event_name=event_name)
    found_event.pop("id", None)
    assert found_event == json.loads(response_creation.text)
