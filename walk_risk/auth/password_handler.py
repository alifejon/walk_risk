"""Password hashing and verification"""

import bcrypt

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class PasswordHandler:
    """Handle password hashing and verification"""

    def __init__(self):
        self.rounds = 12  # bcrypt rounds for security

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        try:
            # Convert password to bytes
            password_bytes = password.encode('utf-8')

            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=self.rounds)
            hashed = bcrypt.hashpw(password_bytes, salt)

            # Return as string
            hashed_str = hashed.decode('utf-8')
            logger.debug("Password hashed successfully")
            return hashed_str
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            raise

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Convert inputs to bytes
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')

            # Verify password
            is_valid = bcrypt.checkpw(password_bytes, hashed_bytes)

            if is_valid:
                logger.debug("Password verification successful")
            else:
                logger.debug("Password verification failed")
            return is_valid
        except Exception as e:
            logger.error(f"Failed to verify password: {e}")
            return False

    def needs_update(self, hashed_password: str) -> bool:
        """Check if password hash needs updating (simplified for direct bcrypt)"""
        try:
            # For direct bcrypt, we can check if the hash format is correct
            # A bcrypt hash should be 60 characters long and start with '$2'
            return not (len(hashed_password) == 60 and hashed_password.startswith('$2'))
        except Exception as e:
            logger.error(f"Failed to check if password needs update: {e}")
            return False

    def update_hash(self, password: str, old_hash: str) -> str:
        """Update password hash if needed"""
        try:
            if self.needs_update(old_hash):
                logger.info("Updating password hash")
                return self.hash_password(password)
            return old_hash
        except Exception as e:
            logger.error(f"Failed to update password hash: {e}")
            raise