import asyncio
import os

from app.schemas.auth import TokenResponseSchema, TokenResponseCallbackSchema
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError
from jwcrypto.jws import InvalidJWSSignature
from keycloak import KeycloakAdmin
from keycloak.exceptions import (
    KeycloakAuthenticationError,
    KeycloakConnectionError,
    KeycloakGetError,
    KeycloakPostError,
)
from keycloak.keycloak_openid import KeycloakOpenID

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

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

def base64_to_pem(base64_string: str) -> str:
    """
    Converting base64 to pem_formatted

    :param str username: Username for register process
    :param str password: Password for register process
    :returns dict token: Token in Privacy-Enhanced Mail formatted public key
    """
    # Remove any whitespace characters
    base64_string = base64_string.strip()

    # Wrap the Base64 string with PEM headers
    pem_header = "-----BEGIN PUBLIC KEY-----\n"
    pem_footer = "-----END PUBLIC KEY-----\n"

    # Split the Base64 string into lines of 64 characters
    pem_body = "\n".join([base64_string[i:i+64] for i in range(0, len(base64_string), 64)])

    # Combine all parts
    pem_formatted = pem_header + pem_body + pem_footer
    return pem_formatted

KEYCLOAK_PUBLIC_KEY = base64_to_pem(base64_string=keycloak_openid.public_key())

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
            return JSONResponse(
                content={"message": "User registered unsuccessfully"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return JSONResponse(
            content={"message": "User registered successfully"},
            status_code=status.HTTP_201_CREATED,
        )
    except KeycloakConnectionError as error:
        return JSONResponse(
            content=f"Connection to Keycloak error - {str(error.error_message)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except KeycloakPostError as error:
        print(f"ERROR={error=}")
        return JSONResponse(
            content="Username already exists",
            status_code=status.HTTP_409_CONFLICT,
        )
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception


async def authenticate_user(username: str, password: str) -> TokenResponseSchema:
    """
    New token generating

    :param str username: Username for register process
    :param str password: Password for register process
    :returns dict token: Token
    """
    try:
        token_response = await keycloak_openid.a_token(username=username, password=password)
        token_response["expires_in"] = str(token_response.get("expires_in", ""))
        token_response["refresh_expires_in"] = str(
            token_response.get("refresh_expires_in", "")
        )
        token_response["not_before_policy"] = str(
            token_response.get("not-before-policy", "")
        )
        return TokenResponseSchema(**token_response)
    except KeycloakAuthenticationError as error:
        return JSONResponse(
            content=f"Invalid credentials - {str(error.error_message)}",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except KeycloakConnectionError as error:
        return JSONResponse(
            content=f"Connection to Keycloak error - {str(error.error_message)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
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
            token_info = keycloak_openid.decode_token(
                token,
                key=KEYCLOAK_PUBLIC_KEY,
                options={"verify_signature": True, "verify_aud": False, "exp": True},
            )

            resource_access = token_info["resource_access"]
            app_property = (
                resource_access[KC_CLIENT_ID] if KC_CLIENT_ID in resource_access else {}
            )
            user_roles = app_property["roles"] if "roles" in app_property else []

            for role in required_roles:
                if role not in user_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role '{role}' is required to perform this action",
                    )

            return token_info
        except (KeycloakGetError, JWTError) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
                headers={"WWW-Authenticate": "Bearer"},
            ) from error

    return verify_token


async def refresh_token(token: str) -> dict[str, str]:
    """
    New token generating after period refresh

    :param str token: Token for refreshing
    :returns dict token: New token
    """
    try:
        refresh_token_response = await keycloak_openid.a_refresh_token(refresh_token=token)
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
    except KeycloakGetError as error:
        return JSONResponse(
            content=str(error.error_message),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except KeycloakPostError as error:
        return JSONResponse(
            content=str(error.error_message),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception


async def verify_token(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    """
    New token verifying

    :returns dict token: New token verification
    """
    try:
        return await keycloak_openid.a_decode_token(token=token)
    except InvalidJWSSignature as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except TypeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except (KeycloakGetError, JWTError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


async def generate_authorization_url() -> str:
    """
    Generating the authorization URL

    :returns str token: New auth url
    """
    auth_url = keycloak_openid.auth_url(
        redirect_uri=f"{REACT_APP_BACKEND_URL}/api/auth/callback", scope="openid"
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
            code=code, redirect_uri=f"{REACT_APP_BACKEND_URL}/api/auth/callback"
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
