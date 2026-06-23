# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
COPY requirements.txt .
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
RUN groupadd -r app && useradd -r -g app app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app . .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://localhost:8000/health'); sys.exit(0)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
