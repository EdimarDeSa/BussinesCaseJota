"""
Gera as verticais automaticamente de acordo com as veriticais registradas na VerticalEnum
"""

from typing import Any

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from ..enums.vertical_enum import VerticalEnum
from ..models import VerticalSchema


@receiver(post_migrate)  # type: ignore
def populate_verticals(sender: Any, **kwargs: dict) -> None:
    if sender.name != "api_portal_jota":
        return

    for value, label in VerticalEnum.choices:
        VerticalSchema.objects.get_or_create(name=label, cod_categoria=value)
