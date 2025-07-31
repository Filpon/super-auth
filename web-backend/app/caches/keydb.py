import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Final

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

load_dotenv()

KEYDB_PORT: Final[str] = os.getenv("KEYDB_PORT")


@asynccontextmanager
async def cache_span(_: FastAPI) -> AsyncIterator[None]:
    """
    Asynchronous context manager for initializing FastAPI caching

    This context manager establishes connection to cache database instance
    and initializes the FastAPI cache with the specified backend

    :param _: FastAPI: The FastAPI application instance. This parameter is
    not used within the context manager but it is included for
    compatibility with FastAPI's dependency injection system

    :yield: The context manager yields control back to the caller
    after initializing the cache. The cache availability within
    the context block
    """
    redis = aioredis.from_url(f"redis://keydb:{KEYDB_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
