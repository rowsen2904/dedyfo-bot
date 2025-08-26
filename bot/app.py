"""Main application setup and routing."""

import logging
from aiogram import Dispatcher, F
from aiogram.filters import CommandStart

from .core.dependencies import get_container
from .handlers import (
    about_me_callback_handler,
    back_callback_handler,
    command_start_handler,
    help_handler,
    my_stats_handler,
    portfolio_callback_handler,
    quotes_callback_handler,
    settings_handler,
)
from .handlers.admin import (
    admin_broadcast_handler,
    admin_broadcast_text_handler,
    admin_clear_cache_handler,
    admin_logs_handler,
    admin_panel_handler,
    admin_stats_handler,
    admin_system_handler,
    admin_users_handler,
    confirm_broadcast_handler,
)
from .handlers.new_features import (
    cat_fact_handler,
    crypto_handler,
    joke_handler,
    news_category_handler,
    news_handler,
    weather_city_handler,
    weather_handler,
    weather_text_handler,
)
from .middleware import (
    AnalyticsMiddleware,
    AuthMiddleware,
    RateLimitMiddleware,
    UserContextMiddleware,
)

logger = logging.getLogger(__name__)


async def setup_dispatcher() -> Dispatcher:
    """Setup dispatcher with middleware and handlers."""
    container = get_container()
    dp = container.dispatcher
    
    # Setup middleware (order matters!)
    dp.message.middleware(UserContextMiddleware())
    dp.callback_query.middleware(UserContextMiddleware())
    
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    dp.message.middleware(AnalyticsMiddleware())
    dp.callback_query.middleware(AnalyticsMiddleware())
    
    # Register handlers
    
    # Command handlers
    dp.message.register(command_start_handler, CommandStart())
    
    # Main navigation handlers
    dp.callback_query.register(back_callback_handler, F.data == "back")
    dp.callback_query.register(about_me_callback_handler, F.data == "about_me")
    dp.callback_query.register(portfolio_callback_handler, F.data == "portfolio")
    dp.callback_query.register(quotes_callback_handler, F.data == "quotes")
    dp.callback_query.register(settings_handler, F.data == "settings")
    
    # Settings handlers
    dp.callback_query.register(help_handler, F.data == "settings:help")
    dp.callback_query.register(my_stats_handler, F.data == "settings:my_stats")
    
    # New feature handlers
    dp.callback_query.register(weather_handler, F.data == "weather")
    dp.callback_query.register(weather_city_handler, F.data.startswith("weather:"))
    dp.callback_query.register(news_handler, F.data == "news")
    dp.callback_query.register(news_category_handler, F.data.startswith("news:"))
    dp.callback_query.register(crypto_handler, F.data == "crypto")
    dp.callback_query.register(joke_handler, F.data == "joke")
    dp.callback_query.register(cat_fact_handler, F.data == "cat_fact")
    
    # Admin handlers
    dp.callback_query.register(admin_panel_handler, F.data == "admin_panel")
    dp.callback_query.register(admin_stats_handler, F.data == "admin:stats")
    dp.callback_query.register(admin_users_handler, F.data == "admin:users")
    dp.callback_query.register(admin_broadcast_handler, F.data == "admin:broadcast")
    dp.callback_query.register(admin_logs_handler, F.data == "admin:logs")
    dp.callback_query.register(admin_system_handler, F.data == "admin:system")
    dp.callback_query.register(admin_clear_cache_handler, F.data == "admin:clear_cache")
    dp.callback_query.register(confirm_broadcast_handler, F.data.startswith("confirm:broadcast"))
    
    # Text handlers
    dp.message.register(weather_text_handler, F.text.regexp(r"^[а-яё\w\s\-]{2,50}$", flags="i"))
    dp.message.register(admin_broadcast_text_handler, F.text)
    
    logger.info("Dispatcher setup completed")
    return dp


async def setup_application():
    """Setup the complete application."""
    container = get_container()
    
    # Initialize all services
    await container.initialize()
    
    # Setup dispatcher
    dp = await setup_dispatcher()
    
    logger.info("Application setup completed")
    return container.bot, dp


async def shutdown_application():
    """Shutdown the application gracefully."""
    container = get_container()
    await container.shutdown()
    logger.info("Application shutdown completed")
