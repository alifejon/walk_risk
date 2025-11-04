"""인증 관련 API 엔드포인트"""

from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...auth import JWTHandler, PasswordHandler
from ...database.connection import get_db
from ...database.models import User

router = APIRouter()

jwt_handler = JWTHandler()
password_handler = PasswordHandler()


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    preferred_mentor: str = "buffett"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: str
    username: str
    email: str
    access_token: str
    refresh_token: str
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """사용자 등록"""
    try:
        # Check if user already exists
        stmt = select(User).where(
            (User.email == request.email) | (User.username == request.username)
        )
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.email == request.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Hash password
        hashed_password = password_handler.hash_password(request.password)

        # Create new user
        new_user = User(
            username=request.username,
            email=request.email,
            hashed_password=hashed_password,
            preferred_mentor=request.preferred_mentor,
            settings={
                "notifications": True,
                "difficulty": "beginner"
            }
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Create tokens
        access_token = jwt_handler.create_access_token(
            user_id=new_user.id,
            username=new_user.username,
            email=new_user.email
        )
        refresh_token = jwt_handler.create_refresh_token(user_id=new_user.id)

        return AuthResponse(
            user_id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=jwt_handler.access_token_expire_minutes * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """사용자 로그인"""
    try:
        # Find user by email
        stmt = select(User).where(User.email == request.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not password_handler.verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Update last active
        user.last_active = datetime.utcnow()
        await db.commit()

        # Create tokens
        access_token = jwt_handler.create_access_token(
            user_id=user.id,
            username=user.username,
            email=user.email
        )
        refresh_token = jwt_handler.create_refresh_token(user_id=user.id)

        return AuthResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=jwt_handler.access_token_expire_minutes * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh")
async def refresh_token(
    request: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """토큰 갱신"""
    try:
        # Verify refresh token
        user_id = jwt_handler.verify_refresh_token(request.refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Get user
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new access token
        access_token = jwt_handler.create_access_token(
            user_id=user.id,
            username=user.username,
            email=user.email
        )

        return {
            "access_token": access_token,
            "expires_in": jwt_handler.access_token_expire_minutes * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout():
    """로그아웃"""
    # For JWT, logout is mainly handled client-side by discarding tokens
    # In a more sophisticated setup, you might maintain a blacklist
    return {"message": "Successfully logged out"}