"""Cache service using Redis."""

import json
import logging
from typing import Any, Optional, Union

import aioredis

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based cache service."""
    
    def __init__(self, redis_client: aioredis.Redis, default_ttl: int = 3600) -> None:
        """Initialize cache service."""
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value is not None:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await self.redis.set(key, serialized_value, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache."""
        try:
            result = await self.redis.incrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None
    
    async def set_with_expiry(self, key: str, value: Any, seconds: int) -> bool:
        """Set value with specific expiry time."""
        return await self.set(key, value, ttl=seconds)
    
    async def get_or_set(
        self, 
        key: str, 
        factory, 
        ttl: Optional[int] = None
    ) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Generate value using factory
        if callable(factory):
            if hasattr(factory, '__call__') and hasattr(factory, '__code__'):
                # Check if it's an async function
                import asyncio
                if asyncio.iscoroutinefunction(factory):
                    new_value = await factory()
                else:
                    new_value = factory()
            else:
                new_value = factory
        else:
            new_value = factory
        
        await self.set(key, new_value, ttl)
        return new_value
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> dict:
        """Get cache statistics."""
        try:
            info = await self.redis.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    # Utility methods for common use cases
    
    async def cache_user_data(self, user_id: int, data: dict, ttl: int = 1800) -> bool:
        """Cache user data with 30-minute default TTL."""
        return await self.set(f"user:{user_id}", data, ttl)
    
    async def get_user_data(self, user_id: int) -> Optional[dict]:
        """Get cached user data."""
        return await self.get(f"user:{user_id}")
    
    async def cache_quote(self, quote: str, ttl: int = 7200) -> bool:
        """Cache quote with 2-hour default TTL."""
        return await self.set("last_quote", quote, ttl)
    
    async def get_cached_quote(self) -> Optional[str]:
        """Get cached quote."""
        return await self.get("last_quote")
    
    async def set_rate_limit(self, user_id: int, limit: int, window: int) -> bool:
        """Set rate limit for user."""
        key = f"rate_limit:{user_id}"
        current = await self.increment(key)
        if current == 1:
            # First request, set expiry
            await self.redis.expire(key, window)
        return current <= limit
