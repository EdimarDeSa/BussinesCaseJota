from celery import shared_task
from django.utils import timezone

from ..enums.status_noticia_enum import StatusNoticiaEnum


@shared_task
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

    mensagem_publicados = f"{noticias.count()} notícias publicadas"

    return mensagem_publicados
