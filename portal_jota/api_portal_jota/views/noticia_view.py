from typing import Any

from django.db import models
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from ..enums.plan_enum import PlanEnum
from ..enums.status_noticia_enum import StatusNoticiaEnum
from ..enums.user_role_enum import UserRoleEnum
from ..models import NoticiaSchema
from ..permissions import CanEditNews, IsEditorOrAdmin
from ..serializers.noticia_serializer import NoticiaSerializer


@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="ID da notícia",
            )
        ]
    )
)
class NoticiaViewSet(viewsets.ModelViewSet):
    serializer_class = NoticiaSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_action_permissions(self) -> list[Any]:
        return {
            "create": [IsEditorOrAdmin()],
            "update": [CanEditNews()],
            "partial_update": [CanEditNews()],
            "destroy": [CanEditNews()],
        }.get(self.action, [])

    def get_permissions(self) -> list[Any]:
        """Combina permissões base com as específicas da ação"""
        return super().get_permissions() + self.get_action_permissions()

    def get_queryset(self) -> list[NoticiaSchema]:
        """
        get_queryset Filtra as noticias de acordo com o perfil do usuário
        >>> Admin: Todas as noticias
        >>> Editor: Todas as noticias do usuário
        >>> Reader: Notas de acordo com o plano e verticais
        """
        user = self.request.user
        queryset = NoticiaSchema.objects.all()

        match user.role:
            case UserRoleEnum.EDITOR:
                return queryset.filter(autor=user)

            case UserRoleEnum.READER:
                base_query = queryset.filter(status=StatusNoticiaEnum.PUBLICADO)

                if user.user_plan.plan == PlanEnum.JOTA_INFO:
                    return base_query.filter(is_pro=False)

                return base_query.filter(
                    models.Q(is_pro=False) | models.Q(is_pro=True, verticais__in=user.user_plan.verticais.all())
                ).distinct()

        return queryset
