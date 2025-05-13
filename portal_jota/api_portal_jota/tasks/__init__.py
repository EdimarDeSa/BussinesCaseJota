from django.conf import settings

match settings.ENV_TYPE:
    case "beat":
        from .publicar_noticia import publicar_noticia

    case "worker":
        from .process_image import process_image
        from .send_email import send_email

    case _:
        from .process_image import process_image
        from .publicar_noticia import publicar_noticia
        from .send_email import send_email
