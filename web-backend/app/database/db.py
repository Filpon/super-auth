import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.configs.logging import configure_logging_handler

load_dotenv()
logger = configure_logging_handler()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

# Async engine creation
engine = create_async_engine(url=DATABASE_URL, echo=True)
# Sessionmaker creation
ASYNC_SESSION_LOCAL = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Session obtaining for service functionality

    :yield AsyncSession session: Asynchronious session object
    """
    async with ASYNC_SESSION_LOCAL() as session:
        yield session
    logger.info("Database session was created")
