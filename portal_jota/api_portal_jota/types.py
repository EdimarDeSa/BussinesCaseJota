from typing import Optional, TypedDict

UserId = str
NoticiaId = str

from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .enums.email_type_enum import EmailTypeEnum


class EmailData(TypedDict):
    email_type: EmailTypeEnum
    to: Optional[list[UserId]]
    news_id: Optional[NoticiaId]


def extend_uuid_schema(description: str = "ID do usuário") -> dict[str, Any]:
    prameters = extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description=description,
            )
        ]
    )
    return {
        "retrieve": prameters,
        "update": prameters,
        "partial_update": prameters,
        "destroy": prameters,
    }
