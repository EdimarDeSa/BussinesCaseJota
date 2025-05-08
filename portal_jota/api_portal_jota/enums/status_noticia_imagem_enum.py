from django.db import models


class StatusNoticiaImagemEnum(models.TextChoices):
    OK = "K", "OK"
    PENDENTE = "P", "Pendente"
    PROCESSANDO_IMAGEM = "I", "Processando imagem"
    ERRO_IMAGEM = "E", "Erro na imagem"
