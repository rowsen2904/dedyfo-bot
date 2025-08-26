"""Dependency injection container."""

import logging
from typing import Optional

import aioredis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from ..config import Settings, get_settings
from ..database import DatabaseManager
from ..services import (
    AnalyticsService,
    CacheService,
    ExternalAPIService,
    NotificationService,
    UserService,
)

logger = logging.getLogger(__name__)


class Container:
    """Dependency injection container."""
    
    def __init__(self) -> None:
        """Initialize container."""
        self._settings: Optional[Settings] = None
        self._bot: Optional[Bot] = None
        self._dispatcher: Optional[Dispatcher] = None
        self._db_manager: Optional[DatabaseManager] = None
        self._redis_client: Optional[aioredis.Redis] = None
        self._cache_service: Optional[CacheService] = None
        self._user_service: Optional[UserService] = None
        self._analytics_service: Optional[AnalyticsService] = None
        self._notification_service: Optional[NotificationService] = None
        self._external_api_service: Optional[ExternalAPIService] = None
    
    # Properties for lazy initialization
    
    @property
    def settings(self) -> Settings:
        """Get settings instance."""
        if self._settings is None:
            self._settings = get_settings()
        return self._settings
    
    @property
    def bot(self) -> Bot:
        """Get bot instance."""
        if self._bot is None:
            self._bot = Bot(
                token=self.settings.bot.token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
        return self._bot
    
    @property
    def dispatcher(self) -> Dispatcher:
        """Get dispatcher instance."""
        if self._dispatcher is None:
            self._dispatcher = Dispatcher()
        return self._dispatcher
    
    @property
    def db_manager(self) -> DatabaseManager:
        """Get database manager instance."""
        if self._db_manager is None:
            self._db_manager = DatabaseManager()
        return self._db_manager
    
    @property
    async def redis_client(self) -> aioredis.Redis:
        """Get Redis client instance."""
        if self._redis_client is None:
            self._redis_client = aioredis.from_url(
                self.settings.redis.url,
                max_connections=self.settings.redis.max_connections,
                decode_responses=True
            )
        return self._redis_client
    
    @property
    async def cache_service(self) -> CacheService:
        """Get cache service instance."""
        if self._cache_service is None:
            redis = await self.redis_client
            self._cache_service = CacheService(
                redis_client=redis,
                default_ttl=self.settings.redis.cache_ttl
            )
        return self._cache_service
    
    @property
    def user_service(self) -> UserService:
        """Get user service instance."""
        if self._user_service is None:
            self._user_service = UserService(db_manager=self.db_manager)
        return self._user_service
    
    @property
    def analytics_service(self) -> AnalyticsService:
        """Get analytics service instance."""
        if self._analytics_service is None:
            self._analytics_service = AnalyticsService(db_manager=self.db_manager)
        return self._analytics_service
    
    @property
    def notification_service(self) -> NotificationService:
        """Get notification service instance."""
        if self._notification_service is None:
            self._notification_service = NotificationService(
                db_manager=self.db_manager,
                bot=self.bot
            )
        return self._notification_service
    
    @property
    def external_api_service(self) -> ExternalAPIService:
        """Get external API service instance."""
        if self._external_api_service is None:
            self._external_api_service = ExternalAPIService(
                quotes_api_url=self.settings.external_apis.quotes_api_url,
                weather_api_key=self.settings.external_apis.weather_api_key,
                news_api_key=self.settings.external_apis.news_api_key
            )
        return self._external_api_service
    
    async def initialize(self) -> None:
        """Initialize all services."""
        logger.info("Initializing application container...")
        
        # Initialize database
        await self.db_manager.initialize()
        
        # Initialize Redis
        await self.redis_client
        
        logger.info("Application container initialized successfully")
    
    async def shutdown(self) -> None:
        """Shutdown all services."""
        logger.info("Shutting down application container...")
        
        # Close Redis connection
        if self._redis_client is not None:
            await self._redis_client.close()
        
        # Close database connection
        if self._db_manager is not None:
            await self._db_manager.close()
        
        # Close bot session
        if self._bot is not None:
            await self._bot.session.close()
        
        logger.info("Application container shutdown complete")
