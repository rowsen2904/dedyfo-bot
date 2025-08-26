"""Main navigation handlers."""

from aiogram.types import CallbackQuery

from ..keyboards.main_keyboard import get_main_keyboard


async def back_callback_handler(callback: CallbackQuery, user=None, **kwargs) -> None:
    """Handle back button navigation."""
    
    # Check if user is admin for proper keyboard
    is_admin = user and user.is_admin if user else False
    
    welcome_text = (
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите интересующий раздел:"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_keyboard(is_admin=is_admin),
        parse_mode="HTML"
    )
    await callback.answer()


async def settings_handler(callback: CallbackQuery, user=None, **kwargs) -> None:
    """Handle settings menu."""
    from ..keyboards.main_keyboard import get_settings_keyboard
    
    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        "Здесь вы можете настроить бота под себя:"
    )
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


async def help_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle help request."""
    help_text = (
        "❓ <b>Помощь</b>\n\n"
        
        "🤖 <b>О боте:</b>\n"
        "Этот бот создан Ровшеном Байрамовым как интерактивное резюме "
        "и демонстрация навыков разработки.\n\n"
        
        "🚀 <b>Основные функции:</b>\n"
        "👤 <b>Обо мне</b> — информация о разработчике\n"
        "💼 <b>Портфолио</b> — проекты и достижения\n"
        "💬 <b>Цитаты</b> — мотивирующие цитаты\n"
        "🌤 <b>Погода</b> — прогноз погоды по городам\n"
        "📰 <b>Новости</b> — свежие новости по категориям\n"
        "₿ <b>Крипто</b> — курсы криптовалют\n"
        "😄 <b>Развлечения</b> — шутки и факты\n"
        "⚙️ <b>Настройки</b> — персонализация бота\n\n"
        
        "💡 <b>Технологии:</b>\n"
        "• Python 3.11+ & aiogram 3.x\n"
        "• PostgreSQL + SQLAlchemy\n"
        "• Redis для кэширования\n"
        "• Docker для развертывания\n"
        "• Структурированное логирование\n"
        "• Мониторинг и аналитика\n\n"
        
        "📧 <b>Контакты:</b>\n"
        "• Telegram: @ded1fo\n"
        "• GitHub: github.com/rowsen2904\n"
        "• LinkedIn: rovshen-bayramov"
    )
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


async def my_stats_handler(callback: CallbackQuery, user=None, **kwargs) -> None:
    """Handle user statistics request."""
    if not user:
        await callback.answer("❌ Пользователь не найден.", show_alert=True)
        return
    
    from ..core.dependencies import get_analytics_service
    
    try:
        analytics_service = await get_analytics_service()
        user_actions = await analytics_service.get_user_actions(user.id, limit=50)
        user_journey = await analytics_service.get_user_journey(user.id, limit=10)
        
        # Calculate stats
        total_actions = len(user_actions)
        unique_features = len(set(action.action for action in user_actions))
        
        # Most used feature
        feature_counts = {}
        for action in user_actions:
            feature_counts[action.action] = feature_counts.get(action.action, 0) + 1
        
        most_used = max(feature_counts.items(), key=lambda x: x[1]) if feature_counts else ("Нет данных", 0)
        
        stats_text = (
            f"📊 <b>Ваша статистика</b>\n\n"
            
            f"👤 <b>Пользователь:</b> {user.full_name}\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"📅 <b>Регистрация:</b> {user.created_at.strftime('%d.%m.%Y')}\n"
            f"🕐 <b>Последняя активность:</b> {user.last_interaction.strftime('%d.%m.%Y %H:%M')}\n\n"
            
            f"📈 <b>Активность:</b>\n"
            f"• Всего сообщений: {user.total_messages}\n"
            f"• Всего действий: {total_actions}\n"
            f"• Использованных функций: {unique_features}\n"
            f"• Любимая функция: {most_used[0]} ({most_used[1]} раз)\n\n"
        )
        
        if user_journey:
            stats_text += "<b>🗂 Последние действия:</b>\n"
            for action in user_journey[:5]:
                action_time = action['timestamp'].strftime('%d.%m %H:%M')
                stats_text += f"• {action['action']} ({action_time})\n"
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики.",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()
