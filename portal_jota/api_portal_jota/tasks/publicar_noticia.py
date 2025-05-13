from celery import shared_task
from django.utils import timezone

from ..enums.email_type_enum import EmailTypeEnum
from ..enums.status_noticia_enum import StatusNoticiaEnum
from .send_email import send_email


@shared_task  # type: ignore
def publicar_noticia() -> str:
    from ..models import NoticiaSchema

    agora = timezone.now()

    noticias = NoticiaSchema.objects.filter(
        status=StatusNoticiaEnum.RASCUNHO,
        data_publicacao__lte=agora,
    )
    for noticia in noticias:
        noticia.status = StatusNoticiaEnum.PUBLICADO
        noticia.save(update_fields=["status"])

        send_email.delay(
            {
                "email_type": EmailTypeEnum.NOTICIA_PUBLICADA,
                "news_id": str(noticia.id),
            }
        )

    mensagem_publicados = f"{noticias.count()} notícias publicadas"

    return mensagem_publicados
