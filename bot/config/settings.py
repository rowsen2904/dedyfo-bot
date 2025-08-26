"""Application settings using Pydantic for validation and type safety."""

import logging
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    
    url: str = Field(..., env="DATABASE_URL")
    echo: bool = Field(False, env="DATABASE_ECHO")
    pool_size: int = Field(10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    
    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis configuration."""
    
    url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    cache_ttl: int = Field(3600, env="CACHE_TTL")
    max_connections: int = Field(10, env="REDIS_MAX_CONNECTIONS")
    
    class Config:
        env_prefix = "REDIS_"


class BotSettings(BaseSettings):
    """Bot configuration."""
    
    token: str = Field(..., env="BOT_TOKEN")
    webhook_url: Optional[str] = Field(None, env="WEBHOOK_URL")
    webhook_secret: Optional[str] = Field(None, env="WEBHOOK_SECRET")
    webhook_path: str = Field("/webhook", env="WEBHOOK_PATH")
    
    # Rate limiting
    rate_limit_requests: int = Field(30, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(60, env="RATE_LIMIT_WINDOW")
    
    # File handling
    max_file_size: int = Field(10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(
        ["jpg", "jpeg", "png", "gif", "pdf", "txt"],
        env="ALLOWED_FILE_TYPES"
    )
    
    @validator("allowed_file_types", pre=True)
    def split_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    class Config:
        env_prefix = "BOT_"


class ExternalAPISettings(BaseSettings):
    """External API configuration."""
    
    quotes_api_url: str = Field("https://api.quotable.io/random", env="QUOTES_API_URL")
    weather_api_key: Optional[str] = Field(None, env="WEATHER_API_KEY")
    news_api_key: Optional[str] = Field(None, env="NEWS_API_KEY")
    
    class Config:
        env_prefix = "API_"


class AdminSettings(BaseSettings):
    """Admin configuration."""
    
    admin_user_ids: List[int] = Field([], env="ADMIN_USER_IDS")
    super_admin_id: Optional[int] = Field(None, env="SUPER_ADMIN_ID")
    
    @validator("admin_user_ids", pre=True)
    def split_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(uid.strip()) for uid in v.split(",") if uid.strip()]
        return v
    
    class Config:
        env_prefix = "ADMIN_"


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration."""
    
    log_level: str = Field("INFO", env="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    prometheus_port: int = Field(8000, env="PROMETHEUS_PORT")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in levels:
            raise ValueError(f"Log level must be one of {levels}")
        return v.upper()
    
    class Config:
        env_prefix = "MONITORING_"


class FeatureFlags(BaseSettings):
    """Feature flags configuration."""
    
    enable_analytics: bool = Field(True, env="ENABLE_ANALYTICS")
    enable_notifications: bool = Field(True, env="ENABLE_NOTIFICATIONS")
    enable_weather: bool = Field(True, env="ENABLE_WEATHER")
    enable_news: bool = Field(True, env="ENABLE_NEWS")
    enable_admin_panel: bool = Field(True, env="ENABLE_ADMIN_PANEL")
    
    class Config:
        env_prefix = "FEATURE_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    bot: BotSettings = BotSettings()
    external_apis: ExternalAPISettings = ExternalAPISettings()
    admin: AdminSettings = AdminSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    features: FeatureFlags = FeatureFlags()
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def log_config(self) -> dict:
        """Get logging configuration."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "structured": {
                    "()": "structlog.stdlib.ProcessorFormatter",
                    "processor": "structlog.dev.ConsoleRenderer",
                },
            },
            "handlers": {
                "default": {
                    "level": self.monitoring.log_level,
                    "class": "logging.StreamHandler",
                    "formatter": "structured" if self.debug else "default",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": self.monitoring.log_level,
                    "propagate": False,
                },
                "aiogram": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
                "sqlalchemy": {
                    "handlers": ["default"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
