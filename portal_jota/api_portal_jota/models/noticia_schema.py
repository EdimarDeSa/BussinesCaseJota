import uuid

from django.db import models
from django.db.models import FileField
from django.db.transaction import atomic
from django.utils import timezone

from ..enums.status_noticia_enum import StatusNoticiaEnum
from ..enums.status_noticia_imagem_enum import StatusNoticiaImagemEnum


def get_upload_to(instance, filename):
    return f"noticias/{instance.id}/{filename}"


def get_image_extension(file: FileField) -> str:
    return file.name.split(".")[-1].lower()


def check_image_type(file: FileField) -> FileField:
    valid_extensions = ["jpg", "jpeg", "png"]
    if not get_image_extension(file) in valid_extensions:
        raise ValueError("Unsupported file extension.")
    return file


class NoticiaSchema(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    titulo = models.CharField(max_length=50)
    subtitulo = models.CharField(max_length=100)
    imagem = models.FileField(upload_to=get_upload_to, blank=True, null=True, validators=[check_image_type])
    status_imagem = models.CharField(
        max_length=1, choices=StatusNoticiaImagemEnum.choices, default=StatusNoticiaImagemEnum.PENDENTE
    )
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField()
    autor = models.ForeignKey("UserSchema", on_delete=models.CASCADE, related_name="noticia")
    status = models.CharField(max_length=1, choices=StatusNoticiaEnum.choices, default=StatusNoticiaEnum.RASCUNHO)
    is_pro = models.BooleanField(default=False)
    verticais = models.ManyToManyField("VerticalSchema")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Noticia: {self.titulo} - {self.data_publicacao} - {self.autor.username}"

    @atomic
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        has_image = bool(self.imagem)

        super().save(*args, **kwargs)

        agora = timezone.now()

        update_fields = kwargs.get("update_fields", [])

        if all(
            [
                not is_new,
                self.status == StatusNoticiaEnum.PUBLICADO,
                "data_publicacao" in update_fields,
                self.data_publicacao > agora,
            ]
        ):
            self.status = StatusNoticiaEnum.RASCUNHO
            self.save(update_fields=["status"])

        imagem_alterada = "imagem" in update_fields

        if any(
            [
                all([is_new, has_image]),
                all([not is_new, imagem_alterada]),
            ]
        ):
            if get_image_extension(self.imagem) != "webp":
                from ..tasks.process_image import process_image

                self.status_imagem = StatusNoticiaImagemEnum.PENDENTE
                process_image.delay(str(self.id))

                if not is_new:
                    self.save(update_fields=["imagem_foi_processada"])
