# 🤖 Dedyfo Bot v2.0

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-green.svg)](https://aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://postgresql.org/)
[![Redis](https://img.shields.io/badge/cache-Redis-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/deployment-Docker-blue.svg)](https://docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A professional Telegram bot with advanced architecture** — a demonstration of senior-level skills in building production-ready applications.

---

## ✨ Features

### 🏗️ **Top-Tier Architecture**
- **Dependency Injection** with a DI container
- **Middleware Pipeline** for request processing
- **Service Layer** for business logic
- **Repository Pattern** for data access
- **Clean Architecture** principles

### 🚀 **Production-Ready**
- **PostgreSQL** with async ORM (SQLAlchemy)
- **Redis** caching with TTL
- **Structured Logging** with JSON format
- **Health Checks** and monitoring
- **Graceful Shutdown** handling
- **Error Handling** with retry mechanisms

### 📊 **Analytics & Monitoring**
- Detailed user analytics
- Performance tracking
- System metrics
- Prometheus ready
- Grafana dashboards

### 🔧 **Functionality**
- **Interactive developer resume**
- **Real-time weather**
- **News** by category
- **Cryptocurrency** rates
- **Motivational quotes**
- **Entertainment content**

### 👑 **Admin Panel**
- User statistics
- Mass messaging
- System management
- Performance monitoring
- Cache management

---

## 🛠️ Tech Stack

| Category      | Technologies                                 |
|--------------|----------------------------------------------|
| **Backend**  | Python 3.11+, aiogram 3.x, aiohttp           |
| **Database** | PostgreSQL, SQLAlchemy (async), Alembic      |
| **Cache**    | Redis, aioredis                              |
| **Deployment**| Docker, docker-compose                      |
| **Monitoring**| Prometheus, Grafana, Sentry                 |
| **Logging**  | structlog, JSON logging                      |
| **Security** | Rate limiting, auth middleware               |
| **Testing**  | pytest, pytest-asyncio                       |
| **Code Quality** | black, flake8, mypy                      |

---

## 🚀 Quick Start

### 1️⃣ Clone the repository
```bash
git clone https://github.com/rowsen2904/dedyfo-bot.git
cd dedyfo-bot
```

### 2️⃣ Set up environment
```bash
# Copy configuration
cp env.example .env

# Edit the .env file
nano .env
```

### 3️⃣ Run with Docker (recommended)
```bash
# Development mode
make docker-dev

# Production mode
make docker-prod
```

### 4️⃣ Local development
```bash
# Install dependencies
make install

# Set up dev environment
make dev

# Run the bot
make run
```

---

## 📋 Configuration

### Main `.env` variables
```bash
# Bot Configuration
BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://yourdomain.com/webhook  # Optional for webhook

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

## 🐳 Docker Deployment

### Development
```bash
# Start all services
docker-compose up --build

# Only bot with dependencies
docker-compose up bot postgres redis
```

### Production
```bash
# Production with monitoring
docker-compose --profile monitoring up -d

# Webhook mode with Nginx
docker-compose --profile webhook up -d
```

### Useful commands
```bash
# Bot logs
make logs

# Access container shell
make docker-shell

# Database migrations
make db-upgrade

# Database backup
make backup
```

---

## 🏗️ Project Structure

```
dedyfo-bot/
├── bot/                          # Main application
│   ├── config/                   # Configuration and settings
│   ├── core/                     # DI container and dependencies
│   ├── database/                 # DB models and connections
│   ├── handlers/                 # Command/event handlers
│   ├── keyboards/                # UI keyboards
│   ├── middleware/               # Middleware components
│   ├── services/                 # Business logic and services
│   ├── texts/                    # Texts and content
│   └── app.py                    # App setup
├── tests/                        # Tests
├── migrations/                   # Alembic migrations
├── monitoring/                   # Monitoring config
├── nginx/                        # Nginx config
├── docker-compose.yml            # Docker environment
├── Dockerfile                    # App image
├── Makefile                      # Dev commands
└── main.py                       # Entry point
```

---

## 📊 Features

### 🎯 **Core Features**
- **👤 About Me** — detailed developer info
- **💼 Portfolio** — projects with descriptions and links
- **🌤 Weather** — up-to-date forecast for any city
- **📰 News** — latest news by category
- **💬 Quotes** — motivational quotes with caching
- **₿ Crypto** — current rates for popular coins
- **😄 Entertainment** — jokes and fun facts

### 🔧 **Administration**
- **📊 Analytics** — detailed usage statistics
- **👥 Users** — user management
- **📢 Broadcasts** — mass notifications
- **⚙️ System** — performance monitoring
- **🗄️ Data** — cache and DB management

### 🔒 **Security**
- **Rate Limiting** — anti-spam protection
- **Auth Middleware** — admin access control
- **Input Validation** — user input validation
- **Error Handling** — safe error processing

---

## 🧪 Testing

```bash
# Run all tests
make test

# Coverage report
pytest --cov=bot --cov-report=html

# Lint code
make lint

# Format code
make format

# Security check
make security-check
```

---

## 📈 Monitoring

### Prometheus metrics
- Request/Response times
- Number of active users
- Errors and exceptions
- Resource usage

### Grafana dashboards
- Bot performance
- User analytics
- System metrics
- Alerts and notifications

### Logging
```python
# Structured JSON logs
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

## 🤝 Development

### Dev environment setup
```bash
# Clone and setup
git clone <repo-url>
cd dedyfo-bot
make quick-start

# Create new migration
make create-migration NAME="add_user_preferences"

# Run in dev mode
make run
```

### Code Style
- **Black** for formatting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

### Git workflow
1. Create a feature branch
2. Make changes
3. Run tests `make check`
4. Create a Pull Request
5. Code Review
6. Merge to main

---

## 📝 API Documentation

### Main endpoints (webhook mode)
```
POST /webhook          # Telegram webhook
GET  /health           # Health check
GET  /metrics          # Prometheus metrics
```

### Main bot commands
```
/start                # Start the bot
/help                 # Help
/admin                # Admin panel (admins only)
```

---

## 🚧 Roadmap

- [ ] **API Gateway** integration
- [ ] **Kubernetes** deployment config
- [ ] **Multi-language** support
- [ ] **Voice Messages** processing
- [ ] **AI Integration** with ChatGPT
- [ ] **Mobile App** for admins
- [ ] **WebUI** admin panel

---

## 💡 Why is this project special?

### 🎯 **Senior Approach**
- Not just "working code", but **architecturally sound solutions**
- **Production-ready** from day one
- **Scalability** and **maintainability**
- **Industry Best Practices**

### 🔥 **Technical Highlights**
- **Async/await** everywhere for performance
- **Type hints** for code reliability
- **Dependency Injection** for testability
- **Structured Logging** for debugging
- **Comprehensive Testing** for quality

### 📈 **Skill Demonstration**
- **System Design** — architecture planning
- **DevOps** — containerization, CI/CD
- **Database Design** — efficient data schemas
- **API Integration** — working with external services
- **Monitoring** — system observability

---

## 👨‍💻 Author

**Rovshen Bayramov** — Backend Developer

- 🔗 **Telegram**: [@ded1fo](https://t.me/ded1fo)
- 💼 **LinkedIn**: [rovshen-bayramov](https://linkedin.com/in/rovshen-bayramov-952a54260/)
- 🐙 **GitHub**: [rowsen2904](https://github.com/rowsen2904)
- 📄 **Resume**: [HH.ru](https://hh.ru/resume/ca3dab4eff0c5a60000039ed1f6c766b446171)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **aiogram** for an excellent Telegram bot framework
- **SQLAlchemy** for a powerful ORM
- **Redis** for fast caching
- **Docker** for deployment simplification
- **Open Source Community** for inspiration

---

<div align="center">
  <h3>⭐ If you like this project — give it a star!</h3>
  <p>This bot demonstrates a professional approach to Telegram bot development</p>
</div>
