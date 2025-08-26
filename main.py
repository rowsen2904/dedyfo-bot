"""
Professional Telegram Bot - Main Application Entry Point

A modern, production-ready Telegram bot built with:
- Advanced architecture with dependency injection
- Professional middleware pipeline
- Database integration with SQLAlchemy
- Redis caching layer
- Comprehensive analytics and monitoring
- Admin panel with system management
- External API integrations
- Rate limiting and security features

Author: Rovshen Bayramov
Version: 2.0.0
"""

import asyncio
import logging
import logging.config
import signal
import sys
from contextlib import asynccontextmanager

import structlog
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.app import setup_application, shutdown_application
from bot.config import get_settings


# Configure structured logging
def setup_logging():
    """Setup structured logging configuration."""
    settings = get_settings()
    logging.config.dictConfig(settings.log_config)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
            if settings.is_production
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


async def setup_webhook(bot: Bot, dp: Dispatcher) -> web.Application:
    """Setup webhook application."""
    settings = get_settings()
    
    if not settings.bot.webhook_url:
        raise ValueError("Webhook URL not configured")
    
    # Set webhook
    await bot.set_webhook(
        url=settings.bot.webhook_url + settings.bot.webhook_path,
        secret_token=settings.bot.webhook_secret,
        drop_pending_updates=True
    )
    
    # Create aiohttp application
    app = web.Application()
    
    # Setup webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.bot.webhook_secret
    )
    
    webhook_requests_handler.register(app, path=settings.bot.webhook_path)
    setup_application(app, dp, bot=bot)
    
    return app


@asynccontextmanager
async def lifespan_context():
    """Application lifespan context manager."""
    logger = structlog.get_logger()
    
    try:
        logger.info("Starting Dedyfo Bot application", version="2.0.0")
        
        # Setup application
        bot, dp = await setup_application()
        
        yield bot, dp
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        raise
    finally:
        logger.info("Shutting down application")
        await shutdown_application()


async def run_polling():
    """Run bot in polling mode."""
    logger = structlog.get_logger()
    
    async with lifespan_context() as (bot, dp):
        logger.info("Starting bot in polling mode")
        
        # Handle graceful shutdown
        async def signal_handler():
            logger.info("Received shutdown signal")
            await bot.session.close()
        
        # Setup signal handlers
        if sys.platform != 'win32':
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(signal_handler()))
        
        try:
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types()
            )
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error("Bot polling error", error=str(e))
            raise


async def run_webhook():
    """Run bot in webhook mode."""
    logger = structlog.get_logger()
    
    async with lifespan_context() as (bot, dp):
        logger.info("Starting bot in webhook mode")
        
        # Setup webhook app
        app = await setup_webhook(bot, dp)
        
        # Run web server
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, host="0.0.0.0", port=8080)
        await site.start()
        
        logger.info("Webhook server started", host="0.0.0.0", port=8080)
        
        try:
            # Keep running
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Webhook server stopped by user")
        finally:
            await runner.cleanup()


def main():
    """Main application entry point."""
    # Setup logging first
    setup_logging()
    logger = structlog.get_logger()
    
    try:
        settings = get_settings()
        
        # Display startup banner
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                       DEDYFO BOT v2.0                       ║
║                                                              ║
║  🤖 Professional Telegram Bot by Rovshen Bayramov           ║
║  🚀 Production-ready architecture                           ║
║  💾 Database: PostgreSQL + SQLAlchemy                       ║
║  🗄️  Cache: Redis                                            ║
║  📊 Analytics & Monitoring                                  ║
║  🔧 Admin Panel                                             ║
║                                                              ║
║  Environment: {settings.environment:<11}                           ║
║  Debug Mode: {str(settings.debug):<12}                             ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Choose runtime mode
        if settings.bot.webhook_url:
            logger.info("Starting in webhook mode")
            asyncio.run(run_webhook())
        else:
            logger.info("Starting in polling mode")
            asyncio.run(run_polling())
            
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
