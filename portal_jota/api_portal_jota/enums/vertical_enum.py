from django.db import models


class VerticalEnum(models.TextChoices):
    PODER = "P", "Poder"
    TRIBUTOS = "T", "Tributos"
    SAUDE = "S", "Saude"
    ENERGIA = "E", "Energia"
    TRABALHISTA = "W", "Trabalhista"
