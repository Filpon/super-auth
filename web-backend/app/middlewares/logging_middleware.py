from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.configs.logging_handler import configure_logging_handler

logger = configure_logging_handler()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses in FastAPI application

    The middleware logs the details of incoming requests and outgoing responses
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Processing the incoming request and logging the details

        This method logs the request method, URL and query parameters before passing
        the request to the next middleware or endpoint. After receiving the response
        it logs the response status code along with the request details

        :param Request request: The incoming request object
        :param Callable[[Request], Awaitable[Response]] call_next: Function calling
        the next middleware or endpoint

        :return Response: The response object returned by the next middleware or endpoint
        """
        request_query_params = request.query_params if request.query_params else "absence"
        # Logging the request details
        logger.info("Request: Method %s - Request URL %s - Query parameters %s",
            request.method,
            request.url,
            request_query_params
        )

        # Calling the next middleware or endpoint
        response: Response = await call_next(request)

        # Logging the response details
        logger.info(
            "Response: Status code %d - Headers %s",
            response.status_code,
            response.raw_headers,
        )

        return response
