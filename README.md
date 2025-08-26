# 🤖 Dedyfo Bot v2.0

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-green.svg)](https://aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://postgresql.org/)
[![Redis](https://img.shields.io/badge/cache-Redis-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/deployment-Docker-blue.svg)](https://docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Профессиональный Telegram-бот с продвинутой архитектурой** — демонстрация навыков senior разработчика в создании production-ready приложений.

---

## ✨ Особенности

### 🏗️ **Архитектура высшего уровня**
- **Dependency Injection** с контейнером зависимостей
- **Middleware Pipeline** для обработки запросов
- **Service Layer** для бизнес-логики
- **Repository Pattern** для работы с данными
- **Clean Architecture** принципы

### 🚀 **Production-Ready**
- **PostgreSQL** с асинхронным ORM (SQLAlchemy)
- **Redis** кэширование с TTL
- **Structured Logging** с JSON форматом
- **Health Checks** и мониторинг
- **Graceful Shutdown** обработка
- **Error Handling** с retry механизмами

### 📊 **Аналитика и Мониторинг**
- Детальная аналитика пользователей
- Трекинг производительности
- Системные метрики
- Prometheus готовность
- Grafana дашборды

### 🔧 **Функциональность**
- **Интерактивное резюме** разработчика
- **Погода** в реальном времени
- **Новости** по категориям
- **Криптовалюты** курсы
- **Мотивационные цитаты**
- **Развлекательный контент**

### 👑 **Админ-панель**
- Статистика пользователей
- Рассылка сообщений
- Управление системой
- Мониторинг производительности
- Очистка кэша

---

## 🛠️ Технический стек

| Категория | Технологии |
|-----------|------------|
| **Backend** | Python 3.11+, aiogram 3.x, aiohttp |
| **Database** | PostgreSQL, SQLAlchemy (async), Alembic |
| **Cache** | Redis, aioredis |
| **Deployment** | Docker, docker-compose |
| **Monitoring** | Prometheus, Grafana, Sentry |
| **Logging** | structlog, JSON logging |
| **Security** | Rate limiting, auth middleware |
| **Testing** | pytest, pytest-asyncio |
| **Code Quality** | black, flake8, mypy |

---

## 🚀 Быстрый старт

### 1️⃣ Клонирование репозитория
```bash
git clone https://github.com/rowsen2904/dedyfo-bot.git
cd dedyfo-bot
```

### 2️⃣ Настройка окружения
```bash
# Копировать конфигурацию
cp env.example .env

# Отредактировать .env файл
nano .env
```

### 3️⃣ Запуск с Docker (рекомендуется)
```bash
# Development режим
make docker-dev

# Production режим
make docker-prod
```

### 4️⃣ Локальная разработка
```bash
# Установка зависимостей
make install

# Настройка dev окружения
make dev

# Запуск бота
make run
```

---

## 📋 Конфигурация

### Основные переменные `.env`
```bash
# Bot Configuration
BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://yourdomain.com/webhook  # Опционально для webhook

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dedyfo_bot

# Redis Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# External APIs
WEATHER_API_KEY=your_weather_api_key
NEWS_API_KEY=your_news_api_key

# Admin Settings
ADMIN_USER_IDS=123456789,987654321
SUPER_ADMIN_ID=123456789

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn
```

---

## 🐳 Docker развертывание

### Development
```bash
# Запуск всех сервисов
docker-compose up --build

# Только бот с зависимостями
docker-compose up bot postgres redis
```

### Production
```bash
# Production с мониторингом
docker-compose --profile monitoring up -d

# Webhook режим с Nginx
docker-compose --profile webhook up -d
```

### Полезные команды
```bash
# Логи бота
make logs

# Доступ к контейнеру
make docker-shell

# Миграции БД
make db-upgrade

# Бэкап БД
make backup
```

---

## 🏗️ Архитектура проекта

```
dedyfo-bot/
├── bot/                          # Основное приложение
│   ├── config/                   # Конфигурация и настройки
│   ├── core/                     # DI контейнер и зависимости  
│   ├── database/                 # Модели БД и подключения
│   ├── handlers/                 # Обработчики команд/событий
│   ├── keyboards/                # Клавиатуры для интерфейса
│   ├── middleware/               # Middleware компоненты
│   ├── services/                 # Бизнес-логика и сервисы
│   ├── texts/                    # Тексты и контент
│   └── app.py                    # Настройка приложения
├── tests/                        # Тесты
├── migrations/                   # Миграции Alembic
├── monitoring/                   # Конфигурация мониторинга
├── nginx/                        # Конфигурация Nginx
├── docker-compose.yml            # Docker окружение
├── Dockerfile                    # Образ приложения
├── Makefile                      # Команды разработки
└── main.py                       # Точка входа
```

---

## 📊 Функциональность

### 🎯 **Основные возможности**
- **👤 Обо мне** — детальная информация о разработчике
- **💼 Портфолио** — проекты с описанием и ссылками
- **🌤 Погода** — актуальный прогноз для любого города
- **📰 Новости** — свежие новости по категориям
- **💬 Цитаты** — мотивационные цитаты с кэшированием
- **₿ Криптовалюты** — актуальные курсы популярных монет
- **😄 Развлечения** — шутки и интересные факты

### 🔧 **Администрирование**
- **📊 Аналитика** — подробная статистика использования
- **👥 Пользователи** — управление пользователями
- **📢 Рассылки** — массовые уведомления
- **⚙️ Система** — мониторинг производительности
- **🗄️ Данные** — управление кэшем и БД

### 🔒 **Безопасность**
- **Rate Limiting** — защита от спама
- **Auth Middleware** — контроль доступа к админ-функциям
- **Input Validation** — валидация пользовательского ввода
- **Error Handling** — безопасная обработка ошибок

---

## 🧪 Тестирование

```bash
# Запуск всех тестов
make test

# Тесты с покрытием
pytest --cov=bot --cov-report=html

# Линтинг кода
make lint

# Форматирование
make format

# Проверка безопасности
make security-check
```

---

## 📈 Мониторинг

### Prometheus метрики
- Request/Response времена
- Количество активных пользователей
- Ошибки и исключения
- Использование ресурсов

### Grafana дашборды
- Производительность бота
- Аналитика пользователей
- Системные метрики
- Алерты и уведомления

### Логирование
```python
# Structured JSON логи
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "bot.handlers.start",
  "message": "User started bot",
  "user_id": 123456789,
  "username": "example_user"
}
```

---

## 🔄 CI/CD

### GitHub Actions workflow
```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: make test
      
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: make deploy-prod
```

---

## 🤝 Разработка

### Настройка dev окружения
```bash
# Клонирование и настройка
git clone <repo-url>
cd dedyfo-bot
make quick-start

# Создание новой миграции
make create-migration NAME="add_user_preferences"

# Запуск в dev режиме
make run
```

### Code Style
- **Black** для форматирования
- **flake8** для линтинга
- **mypy** для type checking
- **pytest** для тестирования

### Git workflow
1. Создать feature branch
2. Внести изменения
3. Запустить тесты `make check`
4. Создать Pull Request
5. Code Review
6. Merge в main

---

## 📝 API Documentation

### Основные эндпоинты (webhook режим)
```
POST /webhook          # Telegram webhook
GET  /health          # Health check
GET  /metrics         # Prometheus metrics
```

### Основные команды бота
```
/start                # Запуск бота
/help                 # Помощь
/admin                # Админ-панель (только для админов)
```

---

## 🚧 Roadmap

- [ ] **API Gateway** интеграция
- [ ] **Kubernetes** деплой конфигурация  
- [ ] **Multi-language** поддержка
- [ ] **Voice Messages** обработка
- [ ] **AI Integration** с ChatGPT
- [ ] **Mobile App** для админов
- [ ] **WebUI** административная панель

---

## 💡 Почему этот проект особенный?

### 🎯 **Senior подход**
- Не просто "работающий код", а **архитектурно продуманное решение**
- **Production-ready** с первого дня
- **Масштабируемость** и **поддерживаемость**
- **Best Practices** индустрии

### 🔥 **Технические highlights**
- **Async/await** везде для производительности
- **Type hints** для надежности кода
- **Dependency Injection** для тестируемости
- **Structured Logging** для отладки
- **Comprehensive Testing** для качества

### 📈 **Демонстрация навыков**
- **System Design** — проектирование архитектуры
- **DevOps** — containerization, CI/CD
- **Database Design** — эффективные схемы данных  
- **API Integration** — работа с внешними сервисами
- **Monitoring** — наблюдаемость системы

---

## 👨‍💻 Автор

**Ровшен Байрамов** — Backend Developer

- 🔗 **Telegram**: [@ded1fo](https://t.me/ded1fo)
- 💼 **LinkedIn**: [rovshen-bayramov](https://linkedin.com/in/rovshen-bayramov-952a54260/)
- 🐙 **GitHub**: [rowsen2904](https://github.com/rowsen2904)
- 📄 **Resume**: [HH.ru](https://hh.ru/resume/ca3dab4eff0c5a60000039ed1f6c766b446171)

---

## 📄 Лицензия

Этот проект лицензирован под MIT License - подробности в файле [LICENSE](LICENSE).

---

## 🙏 Благодарности

- **aiogram** за отличную библиотеку для Telegram ботов
- **SQLAlchemy** за мощный ORM
- **Redis** за быстрое кэширование
- **Docker** за упрощение деплоя
- **Open Source Community** за вдохновение

---

<div align="center">
  <h3>⭐ Если проект понравился — поставьте звезду!</h3>
  <p>Этот бот демонстрирует professional подход к разработке Telegram ботов</p>
</div>
