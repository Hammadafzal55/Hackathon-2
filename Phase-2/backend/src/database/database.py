"""
Database connection and session setup for the Todo backend.
Uses SQLModel with asyncpg for PostgreSQL connectivity.
"""

from sqlmodel import create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def remove_sslmode_param(database_url: str) -> str:
    """
    Remove sslmode parameter from database URL as asyncpg doesn't accept it as a keyword argument.
    Instead, asyncpg uses SSL context for secure connections.
    """
    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query)

    # Remove sslmode parameter if it exists
    if 'sslmode' in query_params:
        del query_params['sslmode']

    # Reconstruct the query string without sslmode
    new_query = urlencode(query_params, doseq=True)

    # Reconstruct the URL without sslmode
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

    return new_url


# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Remove sslmode parameter for asyncpg compatibility
CLEAN_DATABASE_URL = remove_sslmode_param(DATABASE_URL)


# Async engine for PostgreSQL with Neon Serverless
async_engine = create_async_engine(
    CLEAN_DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Validates connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)


# Sync engine for Alembic migrations
sync_engine = create_engine(
    CLEAN_DATABASE_URL.replace("+asyncpg", ""),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)


# Async session maker
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Sync session maker for Alembic
SyncSessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[Session, None]:
    """
    Dependency to get async database session for FastAPI endpoints.
    """
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session() -> Session:
    """
    Function to get sync database session for Alembic migrations.
    """
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_database_url():
    """
    Returns the configured database URL.
    """
    return DATABASE_URL