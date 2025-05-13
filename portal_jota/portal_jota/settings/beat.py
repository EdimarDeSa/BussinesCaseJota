from datetime import timedelta

from celery.schedules import crontab
from django.conf import settings

from .base import *
from .celery import *

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "publicar_noticia": {
        "task": "api_portal_jota.tasks.publicar_noticia.publicar_noticia",
        "schedule": timedelta(seconds=5) if settings.DEBUG else crontab(hour=1),
    },
}
