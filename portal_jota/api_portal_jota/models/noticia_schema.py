import uuid

from django.db import models

from ..enums.status_noticia_enum import StatusNoticiaEnum


class NoticiaSchema(models.Model):
    id_noticia = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, name="id")
    titulo = models.CharField(max_length=50)
    subtitulo = models.CharField(max_length=100)
    imagem = models.FileField(upload_to="noticias/{id_noticia}", blank=True, null=True)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey("UserSchema", on_delete=models.CASCADE, related_name="noticias")
    status = models.CharField(max_length=1, choices=StatusNoticiaEnum.choices, default=StatusNoticiaEnum.RASCUNHO)
    is_pro = models.BooleanField(default=False)
    verticais = models.ManyToManyField("VerticalSchema")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo
