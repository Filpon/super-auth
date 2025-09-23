import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Final, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.types import Backend
from redis import asyncio as aioredis

from app.configs.logging_handler import configure_logging_handler

load_dotenv()

logger = configure_logging_handler()

KEYDB_PASSWORD: Final[Optional[str]] = os.getenv("KEYDB_PASSWORD")
KEYDB_PORT: Final[Optional[str]] = os.getenv("KEYDB_PORT")


@asynccontextmanager
async def cache_span(_: FastAPI) -> AsyncIterator[Backend]:
    """
    Asynchronous context manager for initializing FastAPI caching

    This context manager establishes connection to cache database instance
    and initializes the FastAPI cache with the specified backend

    :param _ FastAPI: The FastAPI application instance. This parameter is
    not used within the context manager but it is included for
    compatibility with FastAPI's dependency injection system

    :yield: The context manager yields control back to the caller
    after initializing the cache. The cache availability within
    the context block
    """
    keydb = aioredis.from_url(f"redis://:{KEYDB_PASSWORD}@keydb:{KEYDB_PORT}")  # type: ignore[no-untyped-call]
    FastAPICache.init(backend=RedisBackend(keydb), prefix="fastapi-cache")
    yield FastAPICache.get_backend()
