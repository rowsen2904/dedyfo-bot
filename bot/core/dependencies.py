"""Dependency injection helpers."""

from functools import lru_cache
from typing import AsyncGenerator

from .container import Container

# Global container instance
_container: Container = None


@lru_cache()
def get_container() -> Container:
    """Get global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


async def get_user_service():
    """Get user service dependency."""
    container = get_container()
    return container.user_service


async def get_analytics_service():
    """Get analytics service dependency."""
    container = get_container()
    return container.analytics_service


async def get_cache_service():
    """Get cache service dependency."""
    container = get_container()
    return await container.cache_service


async def get_notification_service():
    """Get notification service dependency."""
    container = get_container()
    return container.notification_service


async def get_external_api_service():
    """Get external API service dependency."""
    container = get_container()
    return container.external_api_service
