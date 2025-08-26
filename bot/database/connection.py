"""Database connection and session management."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager."""
    
    def __init__(self) -> None:
        """Initialize database manager."""
        self._engine = None
        self._session_factory = None
        self._settings = get_settings()
    
    async def initialize(self) -> None:
        """Initialize database connection."""
        if self._engine is not None:
            return
        
        try:
            self._engine = create_async_engine(
                self._settings.database.url,
                echo=self._settings.database.echo,
                pool_size=self._settings.database.pool_size,
                max_overflow=self._settings.database.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    async def close(self) -> None:
        """Close database connection."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session context manager."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @property
    def engine(self):
        """Get database engine."""
        return self._engine


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with db_manager.get_session() as session:
        yield session
