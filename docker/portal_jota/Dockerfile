# syntax=docker/dockerfile:1.4

FROM python:3.13-alpine AS generator

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN pip install --no-cache-dir poetry-plugin-export \
    && poetry export --without-hashes --only=main,web -f requirements.txt -o requirements.txt

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
        libc6-compat \
        libjpeg-turbo \
        libpng \
        libwebp \
        freetype \
    && rm -rf /var/cache/apk/*

COPY --from=generator /app/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-alpine AS final

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/portal_jota \
    PATH="/app/.local/bin:${PATH}" \
    ENV_TYPE="web"

RUN apk add --no-cache \
        libjpeg-turbo \
        libpng \
        libwebp \
        freetype \
    && adduser -D -h /app -s /bin/sh app \
    && mkdir -p /app/portal_jota \
    && chown -R app:app /app \
    && rm -rf /var/cache/apk/*

WORKDIR /app

COPY --from=builder --chown=app:app /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=app:app portal_jota portal_jota

WORKDIR /app/portal_jota

COPY --chown=app:app docker/portal_jota/entrypoint.sh ./

RUN chmod +x entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT [ "/app/portal_jota/entrypoint.sh" ]'