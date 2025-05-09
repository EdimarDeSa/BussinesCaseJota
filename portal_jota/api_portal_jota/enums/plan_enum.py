from typing import Optional

from django.db import models


class PlanEnum(models.TextChoices):
    JOTA_INFO = "I", "JOTA Info"
    JOTA_PRO = "P", "JOTA Pro"

    @classmethod
    def from_label(cls, label: str) -> Optional["PlanEnum"]:
        """Converte um label para o enum correspondente"""
        try:
            return cls(next(value for value, lab in cls.choices if lab == label))
        except StopIteration:
            return None
