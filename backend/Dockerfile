# =========================================================================
# BizMind Backend Dockerfile
# Production-ready Python 3.12 container running FastAPI + Uvicorn
# =========================================================================

FROM python:3.12-slim

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, deterministic, reproducible dependency installs
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /bin/uv

# Create unprivileged system user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy dependency specifications
COPY pyproject.toml uv.lock ./

# Install production dependencies only into virtualenv
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source code
COPY src ./src
COPY README.md ./

# Create persistent storage directory for SQLite with correct permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to unprivileged user
USER appuser

# Set environment variables
ENV PYTHONPATH="/app/src"
ENV DATABASE_PATH="/app/data/bizmind.db"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn ASGI server
CMD ["/app/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
