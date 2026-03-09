"""
User model for Better Auth integration.
Defines the User entity with Better Auth schema.
"""

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import uuid

if TYPE_CHECKING:
    from .task import Task


class UserBase(SQLModel):
    """
    Base fields for User model following Better Auth schema.
    """
    email: str = Field(unique=True, index=True, nullable=False)
    emailVerified: bool = Field(default=False)


class User(UserBase, table=True):
    """
    User model representing a Better Auth user in the system.
    """
    id: str = Field(primary_key=True)  # Better Auth uses string IDs

    # Better Auth fields
    name: str = Field(default="")
    image: Optional[str] = Field(default=None)

    # Timestamps
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks (temporarily removed for testing without authentication)
    # tasks: List["Task"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """
    Model for creating a new user.
    """
    name: Optional[str] = ""
    image: Optional[str] = None


class UserUpdate(SQLModel):
    """
    Model for updating user information.
    """
    name: Optional[str] = None
    image: Optional[str] = None
    emailVerified: Optional[bool] = None
    updatedAt: Optional[datetime] = None


class UserRead(UserBase):
    """
    Model for reading user information (excluding sensitive data).
    """
    id: str
    name: str
    image: Optional[str]
    createdAt: datetime
    updatedAt: datetime