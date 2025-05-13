import os
from datetime import timedelta
from typing import Any, Optional

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import include, path
from django.utils import timezone
from faker import Faker
from rest_framework import status

from ..enums.plan_enum import PlanEnum
from ..enums.status_noticia_enum import StatusNoticiaEnum
from ..enums.status_noticia_imagem_enum import StatusNoticiaImagemEnum
from ..enums.user_role_enum import UserRoleEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import NoticiaSchema, UserPlanSchema, UserSchema, VerticalSchema
from ..serializers.noticia_serializer import NoticiaSerializer
from ..serializers.user_serializer import UserSerializer
from ..tasks.publicar_noticia import publicar_noticia

PASSWORD = "P@s5W0rd"
faker = Faker("pt_BR")


def generate_user_data(role: UserRoleEnum = UserRoleEnum.READER) -> dict[str, str]:
    return {
        "username": faker.user_name(),
        "email": faker.email(),
        "password": PASSWORD,
        "role": role.label,
    }


def create_user(
    role: UserRoleEnum,
    is_pro: bool = False,
    verticais: Optional[list[VerticalEnum]] = None,
) -> UserSchema:
    user_data = generate_user_data(role)
    serializer = UserSerializer(data=user_data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    if role == UserRoleEnum.READER and is_pro:
        user_plan = UserPlanSchema.objects.filter(cd_user=user.id).first()
        user_plan.plan = PlanEnum.JOTA_PRO
        user_plan.save()
        user_plan.verticais.set(VerticalSchema.objects.filter(cod_categoria__in=verticais))
        user.refresh_from_db()

    return user


def generate_noticia_data(
    is_published: bool = True,
    is_pro: bool = False,
    verticais: list | None = None,
    image: str = "",
) -> dict[str, Any]:
    if verticais is None:
        verticais = faker.random_choices(elements=VerticalEnum.labels, length=faker.random_int(min=1, max=3))

    if not is_published:
        data_publicacao = timezone.now()
    else:
        data_publicacao = faker.date_time_ad(
            start_datetime="+1s", end_datetime="+30s", tzinfo=timezone.get_current_timezone()
        )
    return {
        "titulo": faker.sentence(nb_words=3),
        "subtitulo": faker.sentence(nb_words=5),
        "imagem": image,
        "conteudo": faker.text(),
        "data_publicacao": data_publicacao,
        "is_pro": is_pro,
        "verticais": verticais,
    }


def create_noticia(
    user_editor: UserSchema,
    is_published: bool = True,
    is_pro: bool = False,
    verticais: list | None = None,
    image: str = "",
) -> NoticiaSchema:
    noticia_data = generate_noticia_data(is_published, is_pro, verticais, image)
    noticia_data.update({"autor": user_editor})

    verticais = VerticalSchema.objects.filter(cod_categoria__in=noticia_data.pop("verticais", []))

    noticia = NoticiaSchema.objects.create(**noticia_data)
    noticia.verticais.set(verticais)

    if is_published:
        noticia.status = StatusNoticiaEnum.PUBLICADO.value
        noticia.save()
        noticia.refresh_from_db()

    return noticia
