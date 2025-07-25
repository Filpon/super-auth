import os
from typing import Awaitable, Callable, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIASGIMiddleware
from slowapi.util import get_remote_address

from app.configs.logging import configure_logging_handler
from app.database.db import engine
from app.database.models import Base
from app.routers import auth, events, kafka
from app.routers.kafka import kafka_admin, kafka_producer
from app.services.keycloak import verify_permission, verify_token
from app.utils.handlers import rate_limit_exceeded_handler

load_dotenv()  # Environmental variables
logger = configure_logging_handler()

ORIGINS: Optional[str] = os.getenv("ORIGINS", "")

# FastAPI app creation
app = FastAPI(docs_url="/api/v1/docs", openapi_url="/api/v1/openapi")
limiter = Limiter(key_func=get_remote_address, application_limits=["3/5seconds"])
app.add_middleware(SlowAPIASGIMiddleware)
app.state.limiter = limiter


# Handling RateLimitExceeded exception
@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit_exceeded(
    request: Request, exception_name: RateLimitExceeded
) -> Callable[[Request, Exception], Response | Awaitable[Response]] | JSONResponse:
    """
    Exception handling for RateLimitExceeded.

    This function is called when a request exceeds the allowed rate limit.
    It delegates the handling to the rate_limit_exceeded_handler

    :param request Request: The FastAPI request object
    :param exception_name RateLimitExceeded: The RateLimitExceeded exception instance
    :returns: JSONResponse with 429 status code and error message
    """
    return await rate_limit_exceeded_handler(_=request, __=exception_name)


app.add_exception_handler(RateLimitExceeded, handle_rate_limit_exceeded)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(
    events.router,
    prefix="/api/v1/events",
    tags=["events"],
    dependencies=[Depends(verify_token)],
)
app.include_router(kafka.router, prefix="/api/v1/kafka", tags=["kafka"])

# Configure CORS
origins = ORIGINS.split(sep=",") if ORIGINS else []
logger.info("ORIGINS=%s", ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/check")
async def root() -> Response:
    """
    API Healthcheck

    :returns Response: Response with sucessful status code
    """
    return Response(status_code=status.HTTP_200_OK)


@app.get("/admin")  # Requires the admin role
def call_admin(user: str = Depends(verify_permission(required_roles=["admin"]))) -> str:
    """
    Admin role obtaining

    :param list required_roles: Role admin for calling
    :returns string: Messager for admin user
    """
    return f"Hello, admin {user}"


# Database creation
@app.on_event("startup")
async def startup() -> None:
    """
    Starting database creation

    """
    async with engine.begin() as connector:
        await connector.run_sync(Base.metadata.create_all)
    logger.info("Database creation was finished")
    await kafka_admin.start()
    app.state.producer = await kafka_producer.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Application shutdown

    """
    await kafka_admin.stop()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
