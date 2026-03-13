"""
Database connection and session setup.
Async: asyncpg (FastAPI runtime)
Sync: psycopg2 (Alembic migrations)
Compatible with Neon + HuggingFace Spaces
"""

import os
from dotenv import load_dotenv
from typing import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker



# --------------------------------------------------
# Utils
# --------------------------------------------------

def clean_async_database_url(database_url: str) -> str:
    """
    Remove parameters not supported by asyncpg
    (sslmode, channel_binding, etc.)
    """
    parsed = urlparse(database_url)
    query = parse_qs(parsed.query)

    # asyncpg does NOT support these
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


# --------------------------------------------------
# Base DATABASE URL (SYNC, from ENV)
# --------------------------------------------------

load_dotenv()  # Load environment variables from .env file
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment")
# --------------------------------------------------
# ASYNC DATABASE URL (runtime)
# --------------------------------------------------

ASYNC_DATABASE_URL = clean_async_database_url(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
)

# --------------------------------------------------
# Engines
# --------------------------------------------------

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

sync_engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

# --------------------------------------------------
# Session makers
# --------------------------------------------------

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# --------------------------------------------------
# Dependencies
# --------------------------------------------------

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session() -> Session:
    db = SyncSessionLocal()
    try:
        return db
    finally:
        db.close()


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def get_database_url() -> str:
    return DATABASE_URL
