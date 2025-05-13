#! /bin/sh

cd /app/portal_jota

celery -A portal_jota beat --loglevel=info