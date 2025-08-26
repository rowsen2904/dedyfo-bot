"""Base service class."""

import logging
from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import Base, DatabaseManager

ModelType = TypeVar("ModelType", bound=Base)

logger = logging.getLogger(__name__)


class BaseService(Generic[ModelType]):
    """Base service class for database operations."""
    
    def __init__(self, model: Type[ModelType], db_manager: DatabaseManager) -> None:
        """Initialize base service."""
        self.model = model
        self.db_manager = db_manager
    
    async def get_by_id(self, session: AsyncSession, id_value: int) -> ModelType | None:
        """Get entity by ID."""
        try:
            result = await session.execute(
                select(self.model).where(self.model.id == id_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id_value}: {e}")
            raise
    
    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        """Create new entity."""
        try:
            entity = self.model(**kwargs)
            session.add(entity)
            await session.flush()
            await session.refresh(entity)
            return entity
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    async def update(self, session: AsyncSession, entity: ModelType, **kwargs) -> ModelType:
        """Update entity."""
        try:
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await session.flush()
            await session.refresh(entity)
            return entity
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise
    
    async def delete(self, session: AsyncSession, entity: ModelType) -> None:
        """Delete entity."""
        try:
            await session.delete(entity)
            await session.flush()
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise
