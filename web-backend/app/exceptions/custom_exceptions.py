# exceptions.py
from fastapi import HTTPException
from fastapi import status


class InvalidCredentialsException(HTTPException):
    """
    Exception raised for invalid credentials during authentication.

    This exception is used to indicate that the provided username or password
    is incorrect when attempting to log in.

    :param int status_code: The HTTP status code to return (default is 401).
    :param str detail: A message describing the error (default is "Invalid credentials")
    """

    def __init__(self) -> None:
        """
        Initializes the InvalidCredentialsException with a 401 status code
        and a detail message indicating invalid credentials.
        """
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
