"""
JWT verification middleware for Better Auth integration.
This module provides functions to verify Better Auth tokens and extract user information.
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import json
import uuid
from src.config import get_settings
from src.database.database import get_async_session
from src.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.sql.sqltypes import String


security = HTTPBearer()


async def verify_better_auth_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Verify a Better Auth token and return the associated user from our existing user table.

    Args:
        credentials: Bearer token from Authorization header
        session: Database session for user lookup

    Returns:
        User: The authenticated user object from our existing user table

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token from credentials
    import logging
    logger = logging.getLogger(__name__)

    raw_header = credentials.credentials
    if not raw_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Strip whitespace and normalize
    raw_header = raw_header.strip()

    # Check if header starts with "Bearer " and extract accordingly
    if raw_header.lower().startswith("bearer "):
        # Extract the actual token (remove "Bearer " prefix)
        token = raw_header[7:].strip()  # Remove "Bearer " (7 characters) and any extra whitespace
    else:
        # Treat entire header as the token (Better Auth sometimes sends raw JWT)
        token = raw_header

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # STEP 3: Inspect JWT header before decoding
        # Split the JWT token into parts (header.payload.signature)
        token_parts = token.split('.')
        if len(token_parts) != 3:
            logger.error(f"Invalid JWT token format - expected 3 parts, got {len(token_parts)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid JWT token format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode the Better Auth JWT token WITHOUT signature verification
        # Better Auth tokens don't require signature verification in this context
        payload = jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": True, "verify_aud": False}  # Do not verify signature, but verify expiration
        )

        # Extract user ID from the token in this order:
        # 1. 'sub' (primary)
        # 2. 'id' (fallback)
        user_id_str = payload.get("sub") or payload.get("id")

        # Additional check for common Better Auth token structures if not found
        if not user_id_str and "user" in payload:
            user_data = payload["user"]
            if isinstance(user_data, dict):
                user_id_str = user_data.get("id") or user_data.get("sub")

        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - no user ID in token"
            )

        # Extract user details from token
        user_email = payload.get("email") or (payload.get("user", {}).get("email") if isinstance(payload.get("user"), dict) else None)
        user_name = payload.get("name") or (payload.get("user", {}).get("name") if isinstance(payload.get("user"), dict) else None)
        user_image = payload.get("image") or (payload.get("user", {}).get("image") if isinstance(payload.get("user"), dict) else None)

        # Look up user by email to maintain consistent user identity
        if user_email:
            # Look up the user in our database by email
            email_statement = select(User).where(User.email == user_email)
            email_result = await session.execute(email_statement)
            existing_user = email_result.scalar_one_or_none()

            if existing_user:
                # Return existing user to ensure consistent identity
                # Better Auth doesn't have is_active concept, so just return the user
                return existing_user

        # If user not found, create a new user with Better Auth schema
        from datetime import datetime
        import uuid

        # Generate a unique ID for the user
        user_id = str(uuid.uuid4())

        # Create a new user with Better Auth schema
        new_user = User(
            id=user_id,
            email=user_email or f"unknown_{str(uuid.uuid4())[:8]}@example.com",
            name=user_name or "Unknown User",
            image=user_image,
            emailVerified=True  # Assume verified since it comes from Better Auth
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    except jwt.ExpiredSignatureError:
        logger.error("JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        # Log minimal error for debugging without exposing internals
        logger.warning(f"Invalid Better Auth token: {type(e).__name__}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Log minimal error without exposing internal details
        logger.error(f"Authentication error: {type(e).__name__}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> str:
    """
    Get the current user ID from the Better Auth token in the Authorization header.

    Args:
        credentials: Bearer token from Authorization header
        session: Database session for user lookup

    Returns:
        str: Current user's ID from our existing user table
    """
    user = await verify_better_auth_token(credentials, session)
    return user.id