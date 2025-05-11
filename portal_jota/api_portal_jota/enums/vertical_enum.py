from typing import Optional

from django.db import models


class VerticalEnum(models.TextChoices):
    PODER = "P", "Poder"
    TRIBUTOS = "T", "Tributos"
    SAUDE = "S", "Saude"
    ENERGIA = "E", "Energia"
    TRABALHISTA = "W", "Trabalhista"

    @classmethod
    def from_label(cls, label: str) -> Optional["VerticalEnum"]:
        """Converte um label para o enum correspondente"""
        try:
            return cls(next(value for value, lab in cls.choices if lab == label))
        except StopIteration:
            return None
