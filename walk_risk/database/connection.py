"""Database connection management"""

import asyncio
from typing import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })


class Database:
    """Database connection manager"""

    def __init__(self, database_url: str = None):
        if database_url is None:
            # Default to SQLite for development
            database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./walk_risk.db")

        self.database_url = database_url
        self.engine = None
        self.session_maker = None

    async def connect(self):
        """Connect to database"""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
                pool_pre_ping=True,
                pool_recycle=300,
            )

            # Create session maker
            self.session_maker = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Test connection
            async with self.engine.begin() as conn:
                await conn.run_sync(lambda sync_conn: None)

            logger.info(f"Connected to database: {self.database_url}")

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self):
        """Disconnect from database"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Disconnected from database")

    async def create_tables(self):
        """Create all tables"""
        if not self.engine:
            raise RuntimeError("Database not connected")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        if not self.session_maker:
            raise RuntimeError("Database not connected")

        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()


# Global database instance
database = Database()


async def get_database() -> Database:
    """Get database instance"""
    return database


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (for dependency injection)"""
    async for session in database.get_session():
        yield session