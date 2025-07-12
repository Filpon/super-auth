from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import Token, TokenResponseSchema
from app.services.keycloak import (
    authenticate_user,
    fetch_callback,
    fetch_userinfo_via_token,
    fetch_users,
    generate_authorization_url,
    introspect_token,
    logout,
    oauth2_scheme,
    refresh_token,
    register,
    verify_permission,
    verify_token,
)

router = APIRouter()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    """
    Current user fetching via token

    :param string token: Token creation
    """
    return await fetch_userinfo_via_token(token=token)


@router.post("/register")
async def register_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:  # pylint: disable=W0613
    """
    User registering

    :param OAuth2PasswordRequestForm form_data: Authentication request form
    :returns dict token: Auth token obtaining
    """
    response = await register(form_data.username, form_data.password)
    return response


@router.post("/token", response_model=TokenResponseSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    """
    Token for user auth

    :param OAuth2PasswordRequestForm form_data: Authentication request form
    :returns dict token: Token obtaining
    """
    token = await authenticate_user(
        username=form_data.username, password=form_data.password
    )
    return token


@router.get("/protected")
async def protected_route(_: Token = Depends(verify_token)) -> Dict[str, str]:
    """
    Protected resource testing route.

    The route is protected and requires a valid token to access.

    :param _: The token is used for authentication, automatically
    verified by the `verify_token` dependency.

    :return Dict: Response containing message indicating access to the protected route.
    """
    return {"message": "This is the protected route"}


@router.post("/introspect")
async def introspect(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Introspecting given token.

    The route allows for the introspection of an OAuth2 token to retrieve its details.

    :param token: The OAuth2 token to be introspected, automatically provided by
    the `oauth2_scheme` dependency.

    :return Dict: The result of the token introspection, which may include token
    validity and associated features.
    """
    return await introspect_token(token=token)


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh(token: Token) -> Dict[str, str]:
    """
    Refreshing auth token

    :param Token token: Token for refreshing

    :returns dict new_token: New token after refreshing
    """
    new_token = await refresh_token(token=token.token)
    return new_token


@router.get("/generate-auth")
async def generate_auth() -> RedirectResponse:
    """
    Generating the authorization URL

    :returns RedirectResponse: Response redirecting to callback
    """
    auth_url = await generate_authorization_url()
    return RedirectResponse(url=auth_url)


@router.get("/users")
async def fetch_all_users(_: dict = Depends(verify_permission(["admin"]))) -> List[Dict[str, Any]]:
    """
    Fetching users.

    The route retrieves the list of all users from the database.

    :param _ dict: A dictionary containing the request context, used for permission verification
    :returns List[Dict[str, Any]]: List of users
    """
    return await fetch_users()


@router.get("/callback")
async def callback(request: Request) -> RedirectResponse:
    """
    Callback endpoint to handle the response from Keycloak after user authentication.
    This endpoint receives the authorization code and exchanges it for tokens

    :param Request request: Request for endpoint

    :returns RedirectResponse: Response redirecting to callback
    """
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not found",
        )
    redirect_response = await fetch_callback(code=code)
    return redirect_response


@router.post("/logout")
async def logout_user(token: Token) -> None:
    """
    Class representing logout

    :param str token: Token refreshing from Keycloak
    """
    return await logout(token.token)
