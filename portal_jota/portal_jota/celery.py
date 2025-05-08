import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portal_jota.settings")

app = Celery("portal_jota")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
