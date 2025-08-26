"""Handlers for new advanced features."""

import logging
from typing import Dict

from aiogram import F
from aiogram.types import CallbackQuery, Message

from ..core.dependencies import (
    get_cache_service,
    get_container,
    get_external_api_service,
)
from ..keyboards.main_keyboard import (
    get_main_keyboard,
    get_news_keyboard,
    get_weather_keyboard,
)

logger = logging.getLogger(__name__)


async def weather_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle weather feature request."""
    await callback.message.edit_text(
        "🌤 <b>Прогноз погоды</b>\n\n"
        "Выберите город или укажите свой:",
        reply_markup=get_weather_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


async def weather_city_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle weather for specific city."""
    try:
        city = callback.data.split(":")[1]
        
        if city == "custom":
            await callback.message.edit_text(
                "📍 <b>Ваш город</b>\n\n"
                "Напишите название города для получения прогноза погоды:",
                reply_markup=get_main_keyboard(exclude="weather"),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        # Show loading
        await callback.message.edit_text(
            f"🔄 Получаю погоду для {city}...",
            parse_mode="HTML"
        )
        
        # Get weather data
        external_api = await get_external_api_service()
        weather_data = await external_api.get_weather(city)
        
        if weather_data:
            # Format weather message
            message = (
                f"🌤 <b>Погода в {weather_data['city']}, {weather_data['country']}</b>\n\n"
                f"🌡 Температура: <b>{weather_data['temperature']:.1f}°C</b>\n"
                f"🤔 Ощущается как: <b>{weather_data['feels_like']:.1f}°C</b>\n"
                f"☁️ Состояние: <b>{weather_data['description'].title()}</b>\n"
                f"💧 Влажность: <b>{weather_data['humidity']}%</b>\n"
                f"🌪 Давление: <b>{weather_data['pressure']} гПа</b>\n"
                f"💨 Ветер: <b>{weather_data['wind_speed']} м/с</b>\n"
                f"👁 Видимость: <b>{weather_data['visibility']:.1f} км</b>"
            )
            
            # Cache weather data
            cache_service = await get_cache_service()
            await cache_service.set(f"weather:{city}", weather_data, ttl=1800)  # 30 min cache
            
        else:
            message = f"❌ Не удалось получить погоду для города {city}. Попробуйте еще раз."
        
        await callback.message.edit_text(
            message,
            reply_markup=get_weather_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error handling weather: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при получении погоды. Попробуйте позже.",
            reply_markup=get_weather_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def weather_text_handler(message: Message, **kwargs) -> None:
    """Handle custom city weather request."""
    try:
        city = message.text.strip()
        
        # Validate city name
        if len(city) < 2 or len(city) > 50:
            await message.answer(
                "❌ Неверное название города. Попробуйте еще раз.",
                reply_markup=get_weather_keyboard()
            )
            return
        
        # Show loading
        loading_msg = await message.answer("🔄 Получаю погоду...")
        
        # Get weather data
        external_api = await get_external_api_service()
        weather_data = await external_api.get_weather(city)
        
        if weather_data:
            message_text = (
                f"🌤 <b>Погода в {weather_data['city']}, {weather_data['country']}</b>\n\n"
                f"🌡 Температура: <b>{weather_data['temperature']:.1f}°C</b>\n"
                f"🤔 Ощущается как: <b>{weather_data['feels_like']:.1f}°C</b>\n"
                f"☁️ Состояние: <b>{weather_data['description'].title()}</b>\n"
                f"💧 Влажность: <b>{weather_data['humidity']}%</b>\n"
                f"🌪 Давление: <b>{weather_data['pressure']} гПа</b>\n"
                f"💨 Ветер: <b>{weather_data['wind_speed']} м/с</b>\n"
                f"👁 Видимость: <b>{weather_data['visibility']:.1f} км</b>"
            )
        else:
            message_text = f"❌ Город '{city}' не найден. Проверьте правильность написания."
        
        await loading_msg.edit_text(
            message_text,
            reply_markup=get_weather_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error handling weather text: {e}")
        await message.answer(
            "❌ Произошла ошибка при получении погоды.",
            reply_markup=get_weather_keyboard()
        )


async def news_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle news feature request."""
    await callback.message.edit_text(
        "📰 <b>Последние новости</b>\n\n"
        "Выберите категорию новостей:",
        reply_markup=get_news_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


async def news_category_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle news category selection."""
    try:
        category = callback.data.split(":")[1]
        
        # Show loading
        await callback.message.edit_text(
            f"🔄 Загружаю новости категории '{category}'...",
            parse_mode="HTML"
        )
        
        # Get news data
        external_api = await get_external_api_service()
        news_data = await external_api.get_news(category=category)
        
        if news_data and len(news_data) > 0:
            message = f"📰 <b>Новости: {category.title()}</b>\n\n"
            
            for i, article in enumerate(news_data[:5], 1):
                message += (
                    f"{i}. <b>{article['title']}</b>\n"
                    f"📝 {article['description'][:100]}...\n"
                    f"🔗 <a href='{article['url']}'>Читать полностью</a>\n"
                    f"📅 {article['source']}\n\n"
                )
        else:
            message = f"❌ Не удалось загрузить новости категории '{category}'. Попробуйте позже."
        
        await callback.message.edit_text(
            message,
            reply_markup=get_news_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error handling news: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке новостей.",
            reply_markup=get_news_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def crypto_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle cryptocurrency prices."""
    try:
        # Show loading
        await callback.message.edit_text("🔄 Получаю курсы криптовалют...")
        
        # Get crypto prices
        external_api = await get_external_api_service()
        crypto_data = await external_api.get_crypto_prices()
        
        if crypto_data:
            message = "₿ <b>Курсы криптовалют</b>\n\n"
            
            for crypto_name, prices in crypto_data.items():
                message += (
                    f"<b>{crypto_name}</b>\n"
                    f"💵 ${prices['usd']:,.2f}\n"
                    f"🇷🇺 ₽{prices['rub']:,.2f}\n\n"
                )
            
            # Get exchange rates for context
            rates_data = await external_api.get_exchange_rates()
            if rates_data:
                message += f"💱 USD/RUB: {rates_data['rates']['RUB']:.2f}"
        else:
            message = "❌ Не удалось получить курсы криптовалют. Попробуйте позже."
        
        await callback.message.edit_text(
            message,
            reply_markup=get_main_keyboard(exclude="crypto"),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error handling crypto: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при получении курсов.",
            reply_markup=get_main_keyboard(exclude="crypto"),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def joke_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle joke request."""
    try:
        # Show loading
        await callback.message.edit_text("🔄 Подбираю шутку...")
        
        # Get joke
        external_api = await get_external_api_service()
        joke = await external_api.get_joke()
        
        if joke:
            message = f"😄 <b>Шутка дня</b>\n\n{joke}"
        else:
            message = "❌ Не удалось получить шутку. Попробуйте позже."
        
        await callback.message.edit_text(
            message,
            reply_markup=get_main_keyboard(exclude="joke"),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error handling joke: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при получении шутки.",
            reply_markup=get_main_keyboard(exclude="joke"),
            parse_mode="HTML"
        )
    
    await callback.answer()


async def cat_fact_handler(callback: CallbackQuery, **kwargs) -> None:
    """Handle cat fact request."""
    try:
        # Show loading
        await callback.message.edit_text("🔄 Ищу интересный факт...")
        
        # Get cat fact
        external_api = await get_external_api_service()
        fact = await external_api.get_cat_fact()
        
        if fact:
            message = f"🐱 <b>Факт о котах</b>\n\n{fact}"
        else:
            message = "❌ Не удалось получить факт о котах. Попробуйте позже."
        
        await callback.message.edit_text(
            message,
            reply_markup=get_main_keyboard(exclude="cat_fact"),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error handling cat fact: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при получении факта.",
            reply_markup=get_main_keyboard(exclude="cat_fact"),
            parse_mode="HTML"
        )
    
    await callback.answer()
