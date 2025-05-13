import os
from io import BytesIO

from celery import shared_task
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from ..enums.email_type_enum import EmailTypeEnum
from ..enums.status_noticia_imagem_enum import StatusNoticiaImagemEnum
from ..types import NoticiaId
from .send_email import send_email


@shared_task  # type: ignore
def process_image(noticia_id: NoticiaId) -> str:
    from ..models import NoticiaSchema

    noticia = NoticiaSchema.objects.get(id=noticia_id)
    noticia.status_imagem = StatusNoticiaImagemEnum.PROCESSANDO_IMAGEM
    noticia.save(update_fields=["status_imagem"])

    try:
        old_path = noticia.imagem.path

        image = Image.open(BytesIO(noticia.imagem.read()))
        image = image.convert("RGB")

        image_io = BytesIO()
        image.save(image_io, format="webp")

        new_name = noticia.imagem.name.split(".")[0] + ".webp"

        noticia.imagem = SimpleUploadedFile(
            name=new_name,
            content=image_io.getvalue(),
            content_type="image/webp",
        )

        if os.path.exists(old_path):
            os.remove(old_path)

        noticia.status_imagem = StatusNoticiaImagemEnum.OK
        noticia.save(update_fields=["imagem", "status_imagem"])

        send_email.delay(
            {
                "email_type": EmailTypeEnum.IMAGEM_PROCESSADA,
                "news_id": str(noticia_id),
            }
        )

        return "Done"

    except Exception as e:
        noticia.status_imagem = StatusNoticiaImagemEnum.ERRO_IMAGEM
        noticia.save(update_fields=["status_imagem"])

        send_email.delay(
            {
                "email_type": EmailTypeEnum.ERRO_IMAGEM,
                "news_id": str(noticia_id),
            }
        )
        raise e
