from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.services.keycloak import fetch_userinfo_via_token, oauth2_scheme

from app.schemas.auth import Token, TokenResponseSchema
from app.services.keycloak import (
    authenticate_user,
    fetch_callback,
    generate_authorization_url,
    logout,
    refresh_token,
    register,
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


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh(token: Token) -> dict[str, str]:
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
    await logout(token.token)
