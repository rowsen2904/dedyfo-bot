"""Admin panel handlers for bot management."""

import logging
from datetime import datetime, timedelta
from typing import Dict

from aiogram import F
from aiogram.types import CallbackQuery, Message

from ..core.dependencies import (
    get_analytics_service,
    get_cache_service,
    get_notification_service,
    get_user_service,
)
from ..keyboards.main_keyboard import (
    get_admin_keyboard,
    get_confirmation_keyboard,
    get_main_keyboard,
    get_pagination_keyboard,
)

logger = logging.getLogger(__name__)


async def admin_panel_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle admin panel access."""
    user = kwargs.get('user')
    if not user or not user.is_admin:
        await callback.answer("🚫 У вас нет прав для доступа к админ-панели.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔧 <b>Админ-панель</b>\n\n"
        "Добро пожаловать в панель управления ботом.\n"
        "Выберите нужное действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


async def admin_stats_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle admin statistics."""
    try:
        await callback.message.edit_text("🔄 Собираю статистику...", parse_mode="HTML")
        
        # Get services
        user_service = await get_user_service()
        analytics_service = await get_analytics_service()
        cache_service = await get_cache_service()
        
        # Get user stats
        user_stats = await user_service.get_user_stats()
        
        # Get analytics stats
        engagement_stats = await analytics_service.get_user_engagement_stats()
        popular_features = await analytics_service.get_popular_features(days=7)
        performance_metrics = await analytics_service.get_performance_metrics(days=7)
        
        # Get cache stats
        cache_stats = await cache_service.get_stats()
        
        # Format message
        message = (
            "📊 <b>Статистика бота</b>\n\n"
            
            "👥 <b>Пользователи:</b>\n"
            f"• Всего: {user_stats['total_users']}\n"
            f"• Активных: {user_stats['active_users']}\n"
            f"• Новых сегодня: {user_stats['new_today']}\n"
            f"• Premium: {user_stats['premium_users']}\n"
            f"• Заблокированных: {user_stats['blocked_users']}\n\n"
            
            "📈 <b>Активность:</b>\n"
            f"• Всего действий: {engagement_stats['total_actions']}\n"
            f"• Уникальных пользователей: {engagement_stats['unique_users']}\n"
            f"• Среднее действий на пользователя: {engagement_stats['average_actions_per_user']}\n"
            f"• Активность за 24ч: {engagement_stats['last_24h_activity']}\n\n"
        )
        
        if popular_features:
            message += "🏆 <b>Популярные функции (7 дней):</b>\n"
            for feature in popular_features[:5]:
                message += f"• {feature['feature']}: {feature['usage_count']} использований\n"
            message += "\n"
        
        if performance_metrics and performance_metrics['avg_response_time_ms']:
            message += (
                "⚡ <b>Производительность:</b>\n"
                f"• Среднее время ответа: {performance_metrics['avg_response_time_ms']:.0f}мс\n"
                f"• P95 время ответа: {performance_metrics['p95_response_time_ms']:.0f}мс\n"
                f"• Всего запросов: {performance_metrics['total_requests']}\n\n"
            )
        
        if cache_stats:
            message += (
                "🗄 <b>Кэш:</b>\n"
                f"• Подключенных клиентов: {cache_stats.get('connected_clients', 0)}\n"
                f"• Использовано памяти: {cache_stats.get('used_memory', '0B')}\n"
                f"• Операций в секунду: {cache_stats.get('instantaneous_ops_per_sec', 0)}\n"
            )
        
        await callback.message.edit_text(
            message,
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def admin_users_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle users management."""
    try:
        user_service = await get_user_service()
        
        # Get recent active users
        users = await user_service.get_active_users(limit=10)
        
        message = "👥 <b>Пользователи</b>\n\n"
        
        if users:
            message += "<b>Последние активные пользователи:</b>\n"
            for user in users:
                status_emoji = "👤" if not user.is_admin else "👑"
                last_seen = user.last_interaction.strftime("%d.%m.%Y %H:%M")
                message += (
                    f"{status_emoji} <b>{user.full_name}</b>\n"
                    f"🆔 {user.id} | 📊 {user.total_messages} сообщений\n"
                    f"🕐 Последняя активность: {last_seen}\n\n"
                )
        else:
            message += "Активных пользователей не найдено."
        
        # Add management buttons
        buttons = [
            [callback.InlineKeyboardButton(text="🔍 Поиск пользователей", callback_data="admin:search_users")],
            [callback.InlineKeyboardButton(text="📊 Экспорт данных", callback_data="admin:export_users")],
            [callback.InlineKeyboardButton(text="🔄 Назад", callback_data="admin_panel")]
        ]
        keyboard = callback.InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback.message.edit_text(
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении пользователей.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def admin_broadcast_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle broadcast message setup."""
    await callback.message.edit_text(
        "📢 <b>Рассылка сообщений</b>\n\n"
        "Напишите сообщение для рассылки всем пользователям.\n"
        "Поддерживается HTML-разметка.\n\n"
        "⚠️ <b>Внимание:</b> Сообщение будет отправлено всем активным пользователям.",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


async def admin_broadcast_text_handler(message: Message, **kwargs) -> None:
    """Handle broadcast message text."""
    try:
        user = kwargs.get('user')
        if not user or not user.is_admin:
            await message.answer("🚫 У вас нет прав для рассылки сообщений.")
            return
        
        broadcast_text = message.text or message.caption
        if not broadcast_text:
            await message.answer("❌ Пустое сообщение нельзя отправить в рассылку.")
            return
        
        # Show confirmation
        preview_message = (
            "📢 <b>Предварительный просмотр рассылки:</b>\n\n"
            f"{broadcast_text}\n\n"
            "Отправить это сообщение всем пользователям?"
        )
        
        await message.answer(
            preview_message,
            reply_markup=get_confirmation_keyboard(f"broadcast:{message.message_id}"),
            parse_mode="HTML"
        )
        
        # Store broadcast text in cache
        cache_service = await get_cache_service()
        await cache_service.set(f"broadcast:{message.message_id}", broadcast_text, ttl=3600)
        
    except Exception as e:
        logger.error(f"Error handling broadcast text: {e}")
        await message.answer("❌ Ошибка при подготовке рассылки.")


async def confirm_broadcast_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle broadcast confirmation."""
    try:
        # Extract message ID
        action_data = callback.data.split(":")[1]
        if not action_data.startswith("broadcast:"):
            return
        
        message_id = action_data.split(":")[1]
        
        # Get broadcast text from cache
        cache_service = await get_cache_service()
        broadcast_text = await cache_service.get(f"broadcast:{message_id}")
        
        if not broadcast_text:
            await callback.answer("❌ Сообщение для рассылки не найдено.", show_alert=True)
            return
        
        # Create broadcast notification
        notification_service = await get_notification_service()
        notification = await notification_service.broadcast_announcement(
            title="Рассылка от администрации",
            message=broadcast_text
        )
        
        # Send the broadcast
        await notification_service.send_notification(notification.id)
        
        await callback.message.edit_text(
            "✅ <b>Рассылка отправлена!</b>\n\n"
            "Сообщение отправляется всем активным пользователям.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
        
        # Clean up cache
        await cache_service.delete(f"broadcast:{message_id}")
        
    except Exception as e:
        logger.error(f"Error confirming broadcast: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при отправке рассылки.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def admin_logs_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle logs viewing."""
    try:
        analytics_service = await get_analytics_service()
        
        # Get recent actions
        recent_actions = await analytics_service.get_daily_stats(days=7)
        
        message = "📋 <b>Логи системы</b>\n\n"
        
        if recent_actions:
            message += "<b>Активность за последние 7 дней:</b>\n"
            for day_stats in recent_actions[-7:]:  # Last 7 days
                date_str = day_stats['date'].strftime("%d.%m")
                message += (
                    f"📅 {date_str}: {day_stats['total_actions']} действий, "
                    f"{day_stats['unique_users']} пользователей\n"
                )
        
        # Get popular features
        popular = await analytics_service.get_popular_features(days=7)
        if popular:
            message += "\n<b>Популярные функции:</b>\n"
            for feature in popular[:5]:
                message += f"• {feature['feature']}: {feature['usage_count']}\n"
        
        await callback.message.edit_text(
            message,
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении логов.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def admin_system_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle system information."""
    try:
        import psutil
        import sys
        from datetime import datetime
        
        # System info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Bot uptime (simplified)
        uptime = "N/A"  # Would need to track startup time
        
        message = (
            "⚙️ <b>Система</b>\n\n"
            
            f"🐍 Python: {sys.version.split()[0]}\n"
            f"💻 CPU: {cpu_percent}%\n"
            f"🧠 RAM: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)\n"
            f"💾 Диск: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)\n"
            f"⏰ Uptime: {uptime}\n\n"
            
            "🔧 <b>Управление:</b>\n"
            "• Перезапуск системы\n"
            "• Очистка кэша\n"
            "• Экспорт данных\n"
            "• Резервное копирование"
        )
        
        buttons = [
            [
                callback.InlineKeyboardButton(text="🧹 Очистить кэш", callback_data="admin:clear_cache"),
                callback.InlineKeyboardButton(text="💾 Бэкап", callback_data="admin:backup")
            ],
            [callback.InlineKeyboardButton(text="🔄 Назад", callback_data="admin_panel")]
        ]
        keyboard = callback.InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback.message.edit_text(
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении информации о системе.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def admin_clear_cache_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle cache clearing."""
    try:
        cache_service = await get_cache_service()
        
        # Clear user cache
        user_keys_cleared = await cache_service.clear_pattern("user:*")
        quote_keys_cleared = await cache_service.clear_pattern("last_quote")
        weather_keys_cleared = await cache_service.clear_pattern("weather:*")
        
        total_cleared = user_keys_cleared + quote_keys_cleared + weather_keys_cleared
        
        await callback.message.edit_text(
            f"✅ <b>Кэш очищен</b>\n\n"
            f"Удалено ключей: {total_cleared}\n"
            f"• Пользователи: {user_keys_cleared}\n"
            f"• Цитаты: {quote_keys_cleared}\n"
            f"• Погода: {weather_keys_cleared}",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при очистке кэша.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()
