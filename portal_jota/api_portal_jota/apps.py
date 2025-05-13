from django.apps import AppConfig
from django.conf import settings


class ApiPortalJotaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api_portal_jota"

    def ready(self) -> None:
        if settings.ENV_TYPE not in ["full", "web"]:
            return
        from . import signals
