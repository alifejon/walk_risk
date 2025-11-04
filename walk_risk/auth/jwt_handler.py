"""JWT token handling"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from jose import JWTError, jwt
from pydantic import BaseModel

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    username: str
    email: str
    exp: datetime


class JWTHandler:
    """JWT token handler"""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "walk-risk-secret-key-change-in-production")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

        if self.secret_key == "walk-risk-secret-key-change-in-production":
            logger.warning("Using default JWT secret key. Change in production!")

    def create_access_token(
        self,
        user_id: str,
        username: str,
        email: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token"""
        try:
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

            payload = {
                "sub": user_id,
                "username": username,
                "email": email,
                "exp": expire,
                "type": "access"
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Created access token for user {username}")
            return token

        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise

    def create_refresh_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create refresh token"""
        try:
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

            payload = {
                "sub": user_id,
                "exp": expire,
                "type": "refresh"
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Created refresh token for user {user_id}")
            return token

        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise

    def verify_access_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != "access":
                logger.warning("Invalid token type")
                return None

            user_id = payload.get("sub")
            username = payload.get("username")
            email = payload.get("email")
            exp = datetime.fromtimestamp(payload.get("exp"))

            if not user_id or not username or not email:
                logger.warning("Missing required fields in token")
                return None

            # Check expiration
            if datetime.utcnow() > exp:
                logger.warning("Token has expired")
                return None

            return TokenData(
                user_id=user_id,
                username=username,
                email=email,
                exp=exp
            )

        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            return None

    def verify_refresh_token(self, token: str) -> Optional[str]:
        """Verify refresh token and return user ID"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != "refresh":
                logger.warning("Invalid token type for refresh")
                return None

            user_id = payload.get("sub")
            exp = datetime.fromtimestamp(payload.get("exp"))

            if not user_id:
                logger.warning("Missing user ID in refresh token")
                return None

            # Check expiration
            if datetime.utcnow() > exp:
                logger.warning("Refresh token has expired")
                return None

            return user_id

        except JWTError as e:
            logger.warning(f"JWT decode error for refresh token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying refresh token: {e}")
            return None

    def get_token_expiry_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token expiry information"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = datetime.fromtimestamp(payload.get("exp"))
            now = datetime.utcnow()

            return {
                "expires_at": exp,
                "expires_in_seconds": int((exp - now).total_seconds()),
                "is_expired": now > exp
            }

        except Exception:
            return None