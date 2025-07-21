from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


# Custom exception handler to avoid allowed requests number printing
async def rate_limit_exceeded_handler(_: Request, __: RateLimitExceeded) -> JSONResponse:
    """
    Handler for the RateLimitExceeded exception

    This handler is called when a request exceeds the allowed rate limit.
    It returns a JSON response with 429 status code and error message

    :param _: The FastAPI request object
    :param __: The RateLimitExceeded exception instance
    :returns: JSONResponse with 429 status code and error message
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Too many requests. Please try again later"},
    )
