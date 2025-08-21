from pydantic import BaseModel


class Token(BaseModel):
    """
    Class representing token validation

    """
    token: str


class TokenResponseSchema(BaseModel):
    """
    Validation and structure of Token Response model

    """
    access_token: str
    refresh_token: str
    expires_in: str
    refresh_expires_in: str
    not_before_policy: str


class TokenResponseCallbackSchema(BaseModel):
    """
    Class representing token validation

    """
    access_token: str
    id_token: str


class UserUpdate(BaseModel):
    """
    Class representing user update

    """
    new_password: str


class CustomOAuth2PasswordRequestForm(BaseModel):
    """
    Class representing form for OAuth2 grant type,
    containing necessary fields for user credentials

    """
    username: str
    password: str
