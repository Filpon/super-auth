import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError
from jwcrypto.jws import InvalidJWSObject, InvalidJWSSignature
from jwcrypto.jwt import JWTExpired
from keycloak import KeycloakAdmin
from keycloak.exceptions import (
    KeycloakAuthenticationError,
    KeycloakConnectionError,
    KeycloakGetError,
    KeycloakPostError,
)
from keycloak.keycloak_openid import KeycloakOpenID

from app.schemas.auth import TokenResponseCallbackSchema, TokenResponseSchema

load_dotenv()

REALM = "master"

REACT_APP_DOMAIN_NAME = os.getenv("REACT_APP_DOMAIN_NAME")
KC_HOSTNAME = os.getenv("KC_HOSTNAME")
KC_HOSTNAME_CONTAINER = os.getenv("KC_HOSTNAME_CONTAINER")
KC_PORT = os.getenv("KC_PORT")
KC_REALM_NAME = os.getenv("KC_REALM_NAME")
KC_CLIENT_SECRET_KEY = os.getenv("KC_CLIENT_SECRET_KEY")
KC_CLIENT_ID = os.getenv("KC_CLIENT_ID")
KC_REALM_COMMON_CLIENT = os.getenv("KC_REALM_COMMON_CLIENT")
KC_REALM_COMMON_USER = os.getenv("KC_REALM_COMMON_USER")
KC_REALM_COMMON_USER_PASSWORD = os.getenv("KC_REALM_COMMON_USER_PASSWORD")
KEYCLOAK_ADMIN = os.getenv("KEYCLOAK_ADMIN")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD")
REACT_APP_BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL")


KEYCLOAK_URL = f"{KC_HOSTNAME_CONTAINER}:{KC_PORT}"
KEYCLOAK_CONTAINER_URL = f"{KC_HOSTNAME_CONTAINER}:{KC_PORT}"
KEYCLOAK_BASE_URL = f"{KEYCLOAK_URL}/auth/realms/{KC_REALM_NAME}"
KEYCLOAK_CONTAINER_BASE_URL = f"{KEYCLOAK_CONTAINER_URL}/auth/realms/{KC_REALM_NAME}"

REDIRECT_URI = f"{KEYCLOAK_CONTAINER_URL}/callback"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

keycloak_openid = KeycloakOpenID(
    server_url=f"{KEYCLOAK_CONTAINER_URL}/auth",
    realm_name=KC_REALM_NAME,
    client_id=KC_REALM_COMMON_CLIENT,
    client_secret_key=KC_CLIENT_SECRET_KEY,
    max_retries=10,
)

keycloak_admin = KeycloakAdmin(
    server_url=f"{KEYCLOAK_CONTAINER_URL}/auth",
    username=KC_REALM_COMMON_USER,
    password=KC_REALM_COMMON_USER_PASSWORD,
    user_realm_name=KC_REALM_NAME,
    max_retries=10,
    verify=True,
)


async def register(username: str, password: str) -> JSONResponse:
    """
    User registering

    :param str username: Username for register process
    :param str password: Password for register process
    :returns dict token: Token
    """
    try:
        user_data = {
            "username": username,
            "email": f"{username}@{username}.com",
            "enabled": True,
            "credentials": [
                {"type": "password", "value": password, "temporary": False}
            ],
        }
        # Creation user in Keycloak
        user_id = await keycloak_admin.a_create_user(payload=user_data)

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User {username} registered unsuccessfully",
            )

        return JSONResponse(
            content={"message": f"User {username} registered successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    except KeycloakConnectionError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection to Keycloak error - {str(error.error_message)}",
        ) from error

    except KeycloakAuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error user credentials - {str(error.error_message)}",
        ) from error

    except KeycloakPostError as error:
        error_message_text_lower = error.error_message.decode("utf-8").lower()
        status_code = status.HTTP_400_BAD_REQUEST
        error_content = ""

        if (
            "realm" in error_message_text_lower
            and "not exists" in error_message_text_lower
        ):
            error_content = "Realm does not exist"
            status_code = status.HTTP_401_UNAUTHORIZED
        elif (
            "user" in error_message_text_lower and "exists" in error_message_text_lower
        ):
            error_content = f"Username {username} already exists"
            status_code = status.HTTP_409_CONFLICT
        else:
            error_content = f"Keycloak Post Error - {str(error.error_message)}"

        raise HTTPException(detail=error_content, status_code=status_code) from error

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(exception)} - {exception.__class__}",
        ) from exception


async def authenticate_user(username: str, password: str) -> TokenResponseSchema:
    """
    New token generating

    :param str username: Username for register process
    :param str password: Password for register process
    :returns dict token: Token
    """
    try:
        token_response = await keycloak_openid.a_token(
            username=username, password=password
        )
        token_response["expires_in"] = str(token_response.get("expires_in", ""))
        token_response["refresh_expires_in"] = str(
            token_response.get("refresh_expires_in", "")
        )
        token_response["not_before_policy"] = str(
            token_response.get("not-before-policy", "")
        )
        return TokenResponseSchema(**token_response)

    except KeycloakAuthenticationError as error:
        error_message_text_lower = error.error_message.decode("utf-8").lower()
        if (
            "user" in error_message_text_lower
            and "credentials" in error_message_text_lower
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error user credentials",
            ) from error
        if (
            "client" in error_message_text_lower
            and "credentials" in error_message_text_lower
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error client credentials",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credentials error"
        ) from error

    except KeycloakConnectionError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection to Keycloak container error - {str(error.error_message)}",
        ) from error

    except KeycloakGetError as error:
        error_message_text_lower = error.error_message.decode("utf-8").lower()
        if (
            "realm" in error_message_text_lower
            and "not exists" in error_message_text_lower
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Realm does not exist"
            ) from error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Keycloak Get Error - {str(error.error_message)}",
        ) from error

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(exception)} - {exception.__class__}",
        ) from exception


def verify_permission(required_roles: list):
    """Verify user permissions based on required roles.

    This function returns an asynchronous dependency that verifies if the user
    associated with the provided token has the required roles to perform a specific action.
    If the user does not have the required roles, an HTTP 403 Forbidden error is raised.
    If the token is invalid or cannot be decoded, an HTTP 401 Unauthorized error is raised.

    :param list required_roles: A list of roles that are required to perform the action.
                          If no roles are provided, an empty list is used.

    :return dict[str, str]: A dictionary containing the decoded token information if the user has
             the required roles.

    :raises HTTPException: Raises an HTTP 403 Forbidden error if the user does not
                          have the required roles.
    :raises HTTPException: Raises an HTTP 401 Unauthorized error if the token is
                          invalid or cannot be decoded.
    """
    if not required_roles:
        required_roles = []

    async def verify_permission_token(  # pylint: disable=W0612
        token: str = Depends(oauth2_scheme),
    ) -> dict[str, str]:
        try:
            token_info = await keycloak_openid.a_decode_token(token=token)
            user_groups = token_info.get("groups", [])
            for role in required_roles:
                if role not in user_groups:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role '{role}' is required to perform this action",
                    )

            return token_info
        except JWTExpired as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token period expired",
            ) from error
        except (KeycloakGetError, JWTError) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
            ) from error
        except Exception as exception:
            if (
                exception
                and hasattr(exception, "status_code")
                and hasattr(exception, "detail")
            ):
                raise HTTPException(
                    status_code=exception.status_code,
                    detail=exception.detail,
                ) from exception
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{str(exception)} - {exception.__class__}",
            ) from exception

    return verify_permission_token


async def refresh_token(token: str) -> TokenResponseSchema:
    """
    New token generating after period refresh

    :param str token: Token for refreshing
    :returns dict token: New token
    """
    try:
        refresh_token_response = await keycloak_openid.a_refresh_token(
            refresh_token=token
        )

        refresh_token_response["expires_in"] = str(
            refresh_token_response.get("expires_in", "")
        )
        refresh_token_response["refresh_expires_in"] = str(
            refresh_token_response.get("refresh_expires_in", "")
        )
        refresh_token_response["not_before_policy"] = str(
            refresh_token_response.get("not-before-policy", "")
        )
        return TokenResponseSchema(**refresh_token_response)

    except KeycloakPostError as error:
        error_message_text_lower = error.error_message.decode("utf-8").lower()
        if (
            "refresh" in error_message_text_lower
            and "token" in error_message_text_lower
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error refresh token value",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Credentials error"
        ) from error

    except KeycloakConnectionError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection to Keycloak container error - {str(error.error_message)}",
        ) from error

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(exception)} - {exception.__class__}",
        ) from exception


async def verify_token(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    """
    New token verifying

    :returns dict token: New token verification
    """
    try:
        return await keycloak_openid.a_decode_token(token=token)
    except JWTExpired as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token period expired",
        ) from error

    except InvalidJWSSignature as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    except InvalidJWSObject as error:
        print(f"JWS{error=}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error token format",
        ) from error

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(exception)} - {exception.__class__}",
        ) from exception


async def introspect_token(token: str) -> Dict[str, str]:
    """
    New token verifying

    :returns dict token: New token verification
    """
    try:
        token_info = await keycloak_openid.a_introspect(token=token)

        if not token_info.get("active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not active"
            )

        return token_info

    except Exception as exception:
        # Check if response exists and has a status_code
        if (
            exception
            and hasattr(exception, "status_code")
            and hasattr(exception, "detail")
        ):
            raise HTTPException(
                status_code=exception.status_code,
                detail=exception.detail,
            ) from exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{exception.__class__}",
        ) from exception


async def generate_authorization_url() -> str:
    """
    Generating the authorization URL

    :returns str token: New auth url
    """
    auth_url = keycloak_openid.auth_url(
        redirect_uri=f"{REACT_APP_BACKEND_URL}/api/v1/auth/callback", scope="openid"
    )
    return auth_url


async def fetch_userinfo_via_token(token: str = Depends(oauth2_scheme)):
    """
    Userinfo via token fetching

    :returns dict decoted token: Decoded info
    """
    try:
        return await keycloak_openid.a_decode_token(token=token)
    except KeycloakGetError as error:
        return JSONResponse(
            content=str(error.error_message),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception


async def fetch_callback(code: str = Depends(oauth2_scheme)) -> dict[str, str]:
    """
    Callback and code exchanging

    :returns dict token: New token verification
    """
    try:
        # Exchanging the authorization code for tokens
        token_callback_response = keycloak_openid.token(
            code=code, redirect_uri=f"{REACT_APP_BACKEND_URL}/api/v1/auth/callback"
        )
        token_callback_response["access_token"] = str(
            token_callback_response.get("access_token", "")
        )
        token_callback_response["id_token"] = str(
            token_callback_response.get("id_token", "")
        )

        # Here you can store the tokens in a session or database as needed
        return TokenResponseCallbackSchema(**token_callback_response)
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception


async def fetch_users() -> dict[str, list[dict[str, Any]]]:
    """
    Users fetching

    :returns dict: Users fetching result
    """
    try:
        users_response_result: list[dict[str, Any]] = await keycloak_admin.a_get_users()
        return {"users": users_response_result}
    except KeycloakAuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error user credentials - {str(error.error_message)}",
        ) from error

    except KeycloakPostError as error:
        error_message_text_lower = error.error_message.decode("utf-8").lower()
        if (
            "realm" in error_message_text_lower
            and "not exists" in error_message_text_lower
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Realm does not exist"
            ) from error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Keycloak Post Error - {str(error.error_message)}",
        ) from error

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{exception.__class__}",
        ) from exception


async def delete_user(user_id: str) -> None:
    """
    Deleting user from Keycloak by user ID.

    :param user_id: The ID of the user to delete.
    :raises HTTPException: If there is an error during the deletion process.
    """
    try:
        await keycloak_admin.a_delete_user(user_id=user_id)
    except KeycloakAuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error user credentials - {str(error.error_message)}",
        ) from error

    except KeycloakPostError as error:
        error_message_text_lower = error.error_message.decode("utf-8").lower()
        if (
            "realm" in error_message_text_lower
            and "not exists" in error_message_text_lower
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Realm does not exist"
            ) from error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Keycloak Post Error - {str(error.error_message)}",
        ) from error

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{exception.__class__}",
        ) from exception


async def update_user(user_id: str, user_data: Dict[str, Any]) -> None:
    """
    Updating user in Keycloak by user ID.

    :param user_id: The ID of the user to update.
    :param user_data: Dictionary containing the updated user data.
    :raises HTTPException: If there is an error during the updating process.
    """
    try:
        await keycloak_admin.a_update_user(user_id=user_id, payload=user_data)
    except KeycloakAuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error user credentials - {str(error.error_message)}",
        ) from error

    except KeycloakPostError as error:
        error_message_text_lower = error.error_message.decode("utf-8").lower()
        if (
            "realm" in error_message_text_lower
            and "not exists" in error_message_text_lower
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Realm does not exist"
            ) from error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Keycloak Post Error - {str(error.error_message)}",
        ) from error

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{exception.__class__}",
        ) from exception


async def logout(token: str) -> dict[str, str]:
    """
    Log out the authenticated user

    :param str token: Keycloak token for refreshing
    :returns: Keycloak server response
    :rtype: dict
    """
    try:
        return await keycloak_openid.a_logout(refresh_token=token)
    except KeycloakGetError as error:
        return JSONResponse(
            content=str(error.error_message),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exception)
        ) from exception
