# Multi-stage Docker build for production-ready bot
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user
RUN groupadd -r app && useradd -r -g app app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install pytest pytest-asyncio pytest-mock black flake8 mypy

# Copy source code
COPY . .

# Change ownership to app user
RUN chown -R app:app /app

# Switch to app user
USER app

# Command for development
CMD ["python", "main.py"]

# Production stage
FROM base as production

# Copy only necessary files
COPY bot/ ./bot/
COPY main.py .
COPY pyproject.toml .

# Change ownership to app user
RUN chown -R app:app /app

# Switch to app user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; asyncio.run(__import__('bot.config').config.get_settings())" || exit 1

# Command for production
CMD ["python", "main.py"]

# Labels for metadata
LABEL maintainer="Rovshen Bayramov <rovshen@example.com>" \
      version="2.0.0" \
      description="Professional Telegram Bot with advanced architecture" \
      org.opencontainers.image.title="Dedyfo Bot" \
      org.opencontainers.image.description="Production-ready Telegram bot" \
      org.opencontainers.image.version="2.0.0" \
      org.opencontainers.image.authors="Rovshen Bayramov"
