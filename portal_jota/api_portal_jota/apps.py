import os

from django.apps import AppConfig
from django.conf import settings


class ApiPortalJotaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api_portal_jota"

    def ready(self) -> None:
        if os.getenv("ENV_TYPE", "full").lower() not in ["full", "web"]:
            return
        from . import signals
