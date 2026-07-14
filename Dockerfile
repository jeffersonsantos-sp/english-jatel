# syntax=docker/dockerfile:1

# ---- Build/run stage ----
FROM python:3.11-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching
COPY backend/requirements.txt ./backend/requirements.txt
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r backend/requirements.txt

# Copy source (backend mounts frontend via ../frontend)
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Run as non-root
RUN useradd --create-home --uid 10001 appuser && \
    chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD /opt/venv/bin/python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health').status==200 else 1)" || exit 1

CMD ["/opt/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
