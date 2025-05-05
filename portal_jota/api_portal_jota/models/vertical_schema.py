from django.db import models

from ..enums.vertical_enum import VerticalEnum


class VerticalSchema(models.Model):
    name = models.CharField(max_length=25, unique=True)
    cod_categoria = models.CharField(max_length=1, choices=VerticalEnum.choices, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_cod_categoria_display()
