"""
Authentication utilities for the Todo backend application.
Contains JWT token handling and user authentication functions.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.config import get_settings
from src.models.user import User

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.

    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time

    Returns:
        str: Encoded JWT token
    """
    settings = get_settings()

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    # Use Better Auth secret for consistency with frontend
    encoded_jwt = jwt.encode(to_encode, settings.better_auth_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return the decoded payload.

    Args:
        token (str): JWT token to verify

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    settings = get_settings()

    try:
        # Use Better Auth secret for consistency
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": True, "verify_aud": False}  # Don't verify audience initially
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    """
    Get the current user ID from the JWT token in the Authorization header.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from Authorization header

    Returns:
        UUID: Current user's ID
    """
    token = credentials.credentials
    payload = verify_token(token)

    # Extract user ID from the token - Better Auth may use different claim names
    user_id: str = payload.get("sub") or payload.get("userId") or payload.get("jti") or payload.get("user_id")

    # Additional check for common Better Auth token structures
    if not user_id and "user" in payload:
        user_data = payload["user"]
        if isinstance(user_data, dict):
            user_id = user_data.get("id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - no user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )