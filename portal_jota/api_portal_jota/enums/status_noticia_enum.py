from django.db import models


class StatusNoticiaEnum(models.TextChoices):
    RASCUNHO = "R", "Rascunho"
    PUBLICADO = "P", "Publicado"
