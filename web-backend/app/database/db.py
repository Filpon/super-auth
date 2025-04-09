import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.configs.logging import logger

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Async engine creation
engine = create_async_engine(url=DATABASE_URL, echo=True)

# Sessionmaker creation
ASYNC_SESSION_LOCAL = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """
    Session obtaining for service functionality

    :yield AsyncSession session: Asynchronious session object
    """
    async with ASYNC_SESSION_LOCAL() as session:
        yield session
    logger.info("Database session was created")
