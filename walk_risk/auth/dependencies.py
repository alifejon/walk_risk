"""Authentication dependencies for FastAPI"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .jwt_handler import JWTHandler, TokenData
from ..database.connection import get_db
from ..database.models import User
from sqlalchemy import select

security = HTTPBearer()
jwt_handler = JWTHandler()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Get current authenticated user"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify token
        token_data = jwt_handler.verify_access_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception

        # Get user from database
        stmt = select(User).where(User.id == token_data.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        return user

    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user (can add additional checks here)"""
    # Add any additional user status checks here
    # For now, just return the user
    return current_user


# Convenience dependency for requiring authentication
require_auth = Depends(get_current_active_user)