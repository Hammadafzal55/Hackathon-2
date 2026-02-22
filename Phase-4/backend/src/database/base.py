"""
Base SQLModel class for the Todo backend.
Provides a common base for all database models.
"""

from sqlmodel import SQLModel
from typing import Any
import sqlalchemy as sa
from sqlalchemy.orm import declared_attr


class Base(SQLModel):
    """
    Base class for all SQLModel models in the application.
    Provides common functionality and metadata configuration.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name automatically from class name.
        Converts CamelCase to snake_case for the table name.
        """
        # Convert CamelCase to snake_case
        table_name = ""
        for i, char in enumerate(cls.__name__):
            if char.isupper() and i != 0:
                table_name += "_"
            table_name += char.lower()

        # Handle special case where class ends with "Model"
        if table_name.endswith("_model"):
            table_name = table_name[:-6]

        return table_name

    # SQLAlchemy metadata
    __table_args__ = {"extend_existing": True}

    def dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary, excluding SQLAlchemy internals.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def get_columns(cls) -> list[str]:
        """
        Get list of column names for the model.
        """
        return [column.name for column in cls.__table__.columns]


# Import this to create all tables
def create_db_and_tables(engine):
    """
    Create all database tables based on SQLModel models.
    Should be called during application startup.
    """
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(bind=engine)