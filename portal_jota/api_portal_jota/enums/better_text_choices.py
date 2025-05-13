from typing import Optional

from django.db import models


class BetterTextChoices(models.TextChoices):

    @classmethod
    def from_label(cls, label: str) -> Optional["BetterTextChoices"]:
        try:
            return cls(next(value for value, lab in cls.choices if lab == label))
        except StopIteration:
            return None
