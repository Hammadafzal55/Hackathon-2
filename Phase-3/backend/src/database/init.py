"""
Database initialization module for the Todo backend.
Handles the creation of database tables and initial data setup.
"""

from .database import async_engine
from .base import create_db_and_tables
from sqlmodel import SQLModel
import asyncio
import logging

# Import all models so SQLModel.metadata.create_all picks them up
import src.models.task  # noqa: F401
import src.models.user  # noqa: F401
import src.models.conversation  # noqa: F401
import src.models.message  # noqa: F401


logger = logging.getLogger(__name__)


async def init_db():
    """
    Initialize the database by creating all tables.
    """
    logger.info("Initializing database...")

    # Create all tables defined in SQLModel models
    async with async_engine.begin() as conn:
        # Drop all tables first (use with caution in production!)
        # await conn.run_sync(SQLModel.metadata.drop_all)

        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)

    logger.info("Database initialized successfully")


async def create_initial_data():
    """
    Create initial data for the application if needed.
    This function can be expanded to add default users, categories, etc.
    """
    logger.info("Creating initial data...")

    # Add initial data setup here if needed
    # For example, create default admin user, default categories, etc.

    logger.info("Initial data created successfully")


async def initialize_database():
    """
    Main function to initialize the database and create initial data.
    This should be called during application startup.
    """
    try:
        await init_db()
        await create_initial_data()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    # Run initialization when this module is executed directly
    asyncio.run(initialize_database())