from django.db import models


class PlanEnum(models.TextChoices):
    JOTA_INFO = "I", "JOTA Info"
    JOTA_PRO = "P", "JOTA Pro"
