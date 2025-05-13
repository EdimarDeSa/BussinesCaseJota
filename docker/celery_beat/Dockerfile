# syntax=docker/dockerfile:1.4

FROM python:3.13-alpine AS generator

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN pip install --no-cache-dir poetry-plugin-export \
    && poetry export --without-hashes --only=main,beat -f requirements.txt -o requirements.txt

    
FROM python:3.13-alpine AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apk update && apk upgrade \
    && apk add --no-cache \
        gcc \
        python3-dev \
        musl-dev \
        libffi-dev \
        openssl-dev \
        build-base \
    && rm -rf /var/cache/apk/*

COPY --from=generator /app/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-alpine AS final

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/portal_jota \
    PATH="/app/.local/bin:${PATH}" \
    ENV_TYPE="beat"

RUN adduser -D -h /app -s /bin/sh app \
    && mkdir -p /app/portal_jota \
    && chown -R app:app /app \
    && rm -rf /var/cache/apk/*

WORKDIR /app

COPY --from=builder --chown=app:app /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app/portal_jota

COPY --chown=app:app portal_jota/manage.py manage.py
COPY --chown=app:app portal_jota/portal_jota/celery.py portal_jota/celery.py
COPY --chown=app:app portal_jota/portal_jota/settings portal_jota/settings
COPY --chown=app:app portal_jota/api_portal_jota/apps.py api_portal_jota/apps.py
COPY --chown=app:app portal_jota/api_portal_jota/errors.py api_portal_jota/errors.py
COPY --chown=app:app portal_jota/api_portal_jota/types.py api_portal_jota/types.py
COPY --chown=app:app portal_jota/api_portal_jota/models api_portal_jota/models
COPY --chown=app:app portal_jota/api_portal_jota/enums api_portal_jota/enums

COPY --chown=app:app docker/celery_worker/entrypoint.sh ./

RUN chmod +x entrypoint.sh

USER app

ENTRYPOINT [ "/app/portal_jota/entrypoint.sh" ]'