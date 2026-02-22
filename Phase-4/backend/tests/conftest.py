"""
Pytest configuration and fixtures for MCP tools tests.
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from src.database.base import SQLModel
from src.config import get_settings


def clean_async_database_url(database_url: str) -> str:
    """
    Convert sync database URL to async and remove unsupported parameters.
    """
    # Convert to asyncpg driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    parsed = urlparse(database_url)
    query = parse_qs(parsed.query)

    # asyncpg does NOT support these parameters
    query.pop("sslmode", None)
    query.pop("channel_binding", None)

    clean_query = urlencode(query, doseq=True)

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            clean_query,
            parsed.fragment,
        )
    )


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session for each test function.
    Uses NullPool to avoid connection pooling issues in tests.
    """
    settings = get_settings()

    # Convert database URL to async format
    async_db_url = clean_async_database_url(settings.database_url)

    # Create async engine with NullPool for tests
    engine = create_async_engine(
        async_db_url,
        echo=False,
        poolclass=NullPool
    )

    # Create session factory
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        # No need to rollback here - handlers manage their own transactions

    await engine.dispose()