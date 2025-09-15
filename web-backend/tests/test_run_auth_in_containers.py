import json

import pytest
from fastapi import status

from .data_generating_testing import generate_test_credentials


@pytest.mark.anyio
async def test_health_check(backend_container_runner):
    """
    Testing the endpoint avaibility of the backend service.

    The test sends GET request to the `/check` endpoint
    of the backend service and asserts that the successful response status code,
    indicating that the service is healthy and responsive

    :param backend_container_runner: Fixture that provides way to
    run the backend container and interact with it during tests
    """
    response = await backend_container_runner.get(url="/check", timeout=10)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_generate_auth(backend_container_runner):
    """
    Testing the endpoint of the generating auth

    The test sends GET request to the `/api/v1/auth/generate-auth` endpoint
    of the backend service and asserts that the successful response status code 200 (OK),
    or temporary redirect 307 (Temporary Redirect) indicating that the service is healthy
    and responsive

    :param backend_container_runner: Fixture that provides way to
    run the backend container and interact with it during tests
    """
    response = await backend_container_runner.get(
        url="/api/v1/auth/generate-auth"
    )
    assert response.status_code in {status.HTTP_200_OK, status.HTTP_307_TEMPORARY_REDIRECT}


@pytest.mark.anyio
async def test_auth_generate_calback(backend_container_runner):
    """
    Testing the authentication callback endpoint.

    The test sends GET request to the `/api/v1/auth/callback` endpoint
    with provided authorization code and asserts that the response status
    code indicates an error, either due to bad request or unauthorized access

    :param backend_container_runner: Fixture that provides way to
    run the backend container and interact with it during tests
    """
    response = await backend_container_runner.get(
        url="/api/v1/auth/callback?code=auth_code"
    )
    assert response.status_code in {status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED}


@pytest.mark.anyio
async def test_register_user(backend_container_runner):
    """
    Testing the user registration endpoint of the backend service.

    The test sends POST request to the `/api/v1/auth/register` endpoint
    of the backend service with a generated username and password. It asserts
    that the response status code is either 200 (OK) or 201 (Created),
    indicating that the user registration was successful

    :param backend_container_runner: Fixture that provides way to
    run the backend container and interact with it during tests
    """
    username, password = generate_test_credentials()
    response = await backend_container_runner.post(
        url="/api/v1/auth/register",
        data={"username": username, "password": password},
    )
    assert response.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}


@pytest.mark.anyio
async def test_login(backend_container_runner):
    """
    Testing the user login functionality of the backend service.

    The test first sends POST request to the `/api/v1/auth/register`
    endpoint to create a new user with a generated username and password.
    It then sends POST request to the `/api/v1/auth/token` endpoint
    to log in with the same credentials. The test asserts that the
    response status code is 200 (OK), indicating that the login was
    successful

    :param backend_container_runner: Fixture that provides way to
    run the backend container and interact with it during tests
    """
    username, password = generate_test_credentials()
    await backend_container_runner.post(
        url="/api/v1/auth/register",
        data={"username": username, "password": password},
    )
    response = await backend_container_runner.post(
        url="/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_common_user_refresh_token(backend_container_runner, common_user_tokens):
    """
    Test the token refresh functionality for common users.

    The test sends POST request to the `/api/v1/auth/refresh`
    endpoint with the refresh token of a common user. It asserts that
    the response status code is 200 (OK), indicating that the token
    refresh was successful

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param common_user_tokens: Fixture that provides the token and refresh token
        for common user
    """
    response = await backend_container_runner.post(
        url="/api/v1/auth/refresh",
        json={"token": common_user_tokens["refresh_token"]},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_admin_user_refresh_token(backend_container_runner, admin_user_tokens):
    """
    Test the token refresh functionality for admin users

    The test sends POST request to the `/api/v1/auth/refresh`
    endpoint with the refresh token of an admin user. It asserts that
    the response status code is 200 (OK), indicating that the token
    refresh was successful

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Fixture that provides the tokens and refresh token
        for admin user
    """
    response = await backend_container_runner.post(
        url="/api/v1/auth/refresh",
        json={"token": admin_user_tokens["refresh_token"]},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_common_user_logout(backend_container_runner, admin_user_tokens):
    """
    Test the logout functionality for common users.

    The test sends POST request to the `/api/v1/auth/logout`
    endpoint with the refresh token of a common user. It asserts that
    the response status code is 200 (OK), indicating that the logout
    was successful

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Fixture that provides the refresh token and refresh token
        for common user
    """
    response = await backend_container_runner.post(
        url="/api/v1/auth/logout",
        json={"token": admin_user_tokens["refresh_token"]},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_admin_user_logout(backend_container_runner, admin_user_tokens):
    """
    Test the logout functionality for admin users.

    The test sends POST request to the `/api/v1/auth/logout`
    endpoint with the refresh token of an admin user. It asserts that
    the response status code is 200 (OK), indicating that the logout
    was successful

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Fixture that provides the refresh token and refresh token
        for an admin user
    """
    response = await backend_container_runner.post(
        url="/api/v1/auth/logout",
        json={"token": admin_user_tokens["refresh_token"]},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_fetch_all_users(backend_container_runner, admin_user_tokens):
    """
    The availability of the backend service's user fetching endpoint.

    This test sends GET request to the `/api/v1/auth/users` endpoint
    of the backend service and asserts that the response status code is
    successful, indicating that the service is healthy and responsive

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Dictionary containing the access token and refresh token
        for admin user, used for authentication in the request
    """
    response = await backend_container_runner.get(
        url="/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"}
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_update_user_account(backend_container_runner, admin_user_tokens):
    """
    Testing the update username account functionality.

    The test provides register new user, fetches the list of users to find the
    registered user's ID, updates the user's password, and then verifies
    that the new password works by attempting to obtain token

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Dictionary containing the access token and refresh token
        for admin user, used for authentication in the request
    """
    username, password = generate_test_credentials()
    _, new_password = generate_test_credentials()
    response_register = await backend_container_runner.post(
        url="/api/v1/auth/register",
        data={"username": username, "password": password},
    )
    assert response_register.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}

    response_fetch_users = await backend_container_runner.get(
        url="/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"}
    )
    assert response_fetch_users.status_code == status.HTTP_200_OK
    user_sub_id = ""
    for user in json.loads(response_fetch_users.text)["users"]:
        if username == user["username"]:
            user_sub_id = user["id"]
            break
    response_update_user = await backend_container_runner.put(
        url=f"/api/v1/auth/users/{user_sub_id}",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"},
        json={"new_password": new_password},
    )
    assert response_update_user.status_code == status.HTTP_200_OK
    response = await backend_container_runner.post(
        url="/api/v1/auth/token",
        data={"username": username, "password": new_password},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_delete_user_account(backend_container_runner, admin_user_tokens):
    """
    Testing the functionality of deleting user account.

    The test registers a new user, fetches the list of users to find the
    registered user's ID, deletes the user account, and then verifies that
    the user no longer exists in the user list.

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Dictionary containing the access token and refresh token
        for admin user, used for authentication in the request
    """
    username, password = generate_test_credentials()

    response_register = await backend_container_runner.post(
        url="/api/v1/auth/register",
        data={"username": username, "password": password},
    )
    assert response_register.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}

    response_fetch_users = await backend_container_runner.get(
        url="/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"}
    )
    assert response_fetch_users.status_code == status.HTTP_200_OK
    user_sub_id = ""
    for user in json.loads(response_fetch_users.text)["users"]:
        if username == user["username"]:
            user_sub_id = user["id"]
            break
    response_exclude_user = await backend_container_runner.delete(
        url=f"/api/v1/auth/users/{user_sub_id}",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"}
    )
    assert response_exclude_user.status_code == status.HTTP_200_OK

    response_fetch_users = await backend_container_runner.get(
        url="/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"}
    )
    assert response_fetch_users.status_code == status.HTTP_200_OK

    for user in json.loads(response_fetch_users.text)["users"]:
        if username == user["username"]:
            assert False


@pytest.mark.anyio
async def test_common_user_protected_route(backend_container_runner, common_user_tokens):
    """
    Testing the protected route for common users.

    The test sends GET request to the `/api/v1/auth/protected` endpoint
    using the access token of a common user. It asserts that the response status
    code is successful, indicating that common user has access to the protected
    resource

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param common_user_tokens: Dictionary containing the access token and refresh token
        for common user, used for authentication in the request
    """
    response = await backend_container_runner.get(
        url="/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {common_user_tokens['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.text).get("message", "") == "This is the protected route"


@pytest.mark.anyio
async def test_admin_user_protected_route(backend_container_runner, admin_user_tokens):
    """
    Testing the protected route for admin users.

    The test sends GET request to the `/api/v1/auth/protected` endpoint
    using the access token of an admin user. It asserts that the response status
    code is successful, indicating that admin user has access to the protected
    resource

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Dictionary containing the access token and refresh token
        for admin user, used for authentication in the request
    """
    response = await backend_container_runner.get(
        url="/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.text).get("message", "") == "This is the protected route"


@pytest.mark.anyio
async def test_common_user_introspect_token(backend_container_runner, common_user_tokens):
    """
    Testing the token introspection endpoint.

    The test sends POST request to the `/api/v1/auth/introspect` endpoint
    using the access token of an admin user. It asserts that the response status
    code is successful, indicating that the token introspection was processed
    correctly

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param common_user_tokens: Dictionary containing the access token and refresh token
        for admin user, used for authentication in the request
    """
    response = await backend_container_runner.post(
        url="/api/v1/auth/introspect",
        headers={"Authorization": f"Bearer {common_user_tokens['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(json.loads(response.text).get("groups", []))
    assert "admin" not in json.loads(response.text).get("groups", [])


@pytest.mark.anyio
async def test_admin_user_introspect_token(backend_container_runner, admin_user_tokens):
    """
    Testing the token introspection endpoint.

    The test sends POST request to the `/api/v1/auth/introspect` endpoint
    using the access token of admin user. It asserts that the response status
    code is successful, indicating that the token introspection was processed
    correctly

    :param backend_container_runner: Fixture that provides a way to
        run the backend container and interact with it during tests
    :param admin_user_tokens: Dictionary containing the access token and refresh token
        for admin user, used for authentication in the request
    """
    response = await backend_container_runner.post(
        url="/api/v1/auth/introspect",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "admin" in json.loads(response.text).get("groups", [])


@pytest.mark.anyio
async def test_admin_check(backend_container_runner, admin_user_tokens):
    """
    Testing the endpoint avaibility of the backend service

    The test sends GET request to the `/admin` endpoint
    of the backend service and asserts that the successful response status code,
    indicating that the service is healthy and responsive

    :param backend_container_runner: Fixture that provides way to
    run the backend container and interact with it during tests
    :param admin_user_tokens: Dictionary containing the access token and refresh token
        for admin user, used for authentication in the request
    """
    response = await backend_container_runner.get(
        url="/admin",
        headers={"Authorization": f"Bearer {admin_user_tokens['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "Hello, admin" in response.text
