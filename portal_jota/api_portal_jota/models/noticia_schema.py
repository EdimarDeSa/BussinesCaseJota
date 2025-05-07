import uuid

from django.db import models

from ..enums.status_noticia_enum import StatusNoticiaEnum


def get_upload_to(instance, filename):
    return f"noticias/{instance.id}/{filename}"


class NoticiaSchema(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    titulo = models.CharField(max_length=50)
    subtitulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to=get_upload_to, blank=True, null=True)
    imagem_foi_processada = models.BooleanField(default=False)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField()
    autor = models.ForeignKey("UserSchema", on_delete=models.CASCADE, related_name="noticia")
    status = models.CharField(max_length=1, choices=StatusNoticiaEnum.choices, default=StatusNoticiaEnum.RASCUNHO)
    is_pro = models.BooleanField(default=False)
    verticais = models.ManyToManyField("VerticalSchema")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: Criar campo para imagem processada
    # TODO: Criar task para processamento de imagem
    # TODO: Criar task para atualização de status
    # TODO: Criar task para atualização de status

    def __str__(self):
        return f"Noticia: {self.titulo} - {self.data_publicacao} - {self.autor.username}"
