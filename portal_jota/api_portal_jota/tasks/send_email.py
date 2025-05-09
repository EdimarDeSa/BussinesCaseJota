from celery import shared_task

from ..enums.email_type_enum import EmailTypeEnum
from ..enums.user_role_enum import UserRoleEnum
from ..models import NoticiaSchema, UserSchema, VerticalSchema
from ..types import EmailData


@shared_task
def send_email(email_data: EmailData) -> str:
    """
    Send Email Service

    Args:
        email_data (EmailData): {
            "email_type": EmailTypeEnum,
            "to": Optional[list[UserId]],
            "news_id": Optional[NoticiaId]
        }

    """

    def get_email_list(verticais: list[VerticalSchema]) -> list[UserSchema]:
        users = UserSchema.objects.filter(role=UserRoleEnum.READER)
        if verticais:
            users = users.filter(user_plan__verticais__in=verticais)

        return list(users.values_list("email", flat=True))

    send_to: str | list[str]
    subject: str | list[str]
    body: str
    email_type = EmailTypeEnum(email_data["email_type"])

    match email_type:
        case EmailTypeEnum.BEM_VINDO:
            user = UserSchema.objects.get(id=email_data["to"][0])

            send_to = user.email
            subject = "Bem vindo ao portal jota!"
            body = f"""
            Olá {user.username}, seja bem vindo ao portal jota!
            """

        case EmailTypeEnum.NOTICIA_PUBLICADA:
            noticia = NoticiaSchema.objects.get(id=email_data["news_id"])

            verticais = noticia.verticais.all() if noticia.is_pro else None

            autor_email = noticia.autor.email
            send_to = [autor_email]
            send_to += get_email_list(verticais)

            subject = f"Nova noticia para o portal jota! - {noticia.titulo}"
            body = f"""
            Olá, seja bem vindo ao portal jota!

            Temos uma nova noticia para você!

            Título: {noticia.titulo}
            Link: http://localhost:8000/noticias/{noticia.id}
            """

        case EmailTypeEnum.NOTICIA_DESATIVADA:
            noticia = NoticiaSchema.objects.get(id=email_data["news_id"])

            send_to = noticia.autor.email

            subject = f"Noticia desativada no portal jota! - {noticia.titulo}"
            body = f"""
            Olá, {noticia.autor.username}!

            Sua noticia {noticia.id} foi desativada devido a alteração da data de publicação.
            
            Título: {noticia.titulo}
            Link: http://localhost:8000/noticias/{noticia.id}
            """

        case EmailTypeEnum.IMAGEM_PROCESSADA:
            noticia = NoticiaSchema.objects.get(id=email_data["news_id"])

            send_to = noticia.autor.email

            subject = f"Imagem processada no portal jota! - {noticia.titulo}"
            body = f"""
            Olá, {noticia.autor.username}!

            A imagem da noticia {noticia.id} foi processada com sucesso e ja pode ser visualizada.
            
            Título: {noticia.titulo}
            Link: http://localhost:8000/noticias/{noticia.id}
            """

        case EmailTypeEnum.ERRO_IMAGEM:
            noticia = NoticiaSchema.objects.get(id=email_data["news_id"])

            send_to = noticia.autor.email

            subject = f"Imagem com erro no portal jota! - {noticia.titulo}"
            body = f"""
            Olá, {noticia.autor.username}!

            A imagem da noticia {noticia.id} foi processada com erro.
            
            Título: {noticia.titulo}
            Link: http://localhost:8000/noticias/{noticia.id}
            """

        case _:
            return "Tipo de email inválido"

    print(f'Enviando email para {send_to} com assunto "{subject}" e corpo"{body}"')
    return f"Email {email_type.name} enviado para {send_to}"
