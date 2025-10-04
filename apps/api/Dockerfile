FROM python:3.11-slim

ARG APP_VERSION=0.1.0
ARG GIT_SHA=dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app \
    PORT=8000

WORKDIR ${APP_HOME}

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app ./app

LABEL org.opencontainers.image.source="${GITHUB_SERVER_URL:-}" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.title="Cloud Native Infra Simulation API"

# Create non-root user
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser ${APP_HOME}
USER appuser

EXPOSE ${PORT}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


