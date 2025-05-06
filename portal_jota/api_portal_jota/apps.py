from django.apps import AppConfig


class ApiPortalJotaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api_portal_jota"

    def ready(self):
        from . import signals
