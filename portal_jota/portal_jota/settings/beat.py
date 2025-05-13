from datetime import timedelta

from celery.schedules import crontab

from .base import *
from .base import DEBUG  # Para evitar erro de linter
from .worker import *

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "publicar_noticia": {
        "task": "api_portal_jota.tasks.publicar_noticia.publicar_noticia",
        "schedule": timedelta(seconds=5) if DEBUG else crontab(hour=1),
    },
}
