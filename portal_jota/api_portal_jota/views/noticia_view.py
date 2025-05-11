from typing import Any

from django.db import models
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ..enums.plan_enum import PlanEnum
from ..enums.status_noticia_enum import StatusNoticiaEnum
from ..enums.user_role_enum import UserRoleEnum
from ..enums.vertical_enum import VerticalEnum
from ..errors import ImageError
from ..models import NoticiaSchema, UserSchema
from ..permissions import IsEditorOrAdmin
from ..serializers.noticia_serializer import NoticiaSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="id",
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.UUID,
            description="ID da notícia",
        )
    ]
)
class NoticiaViewSet(viewsets.ModelViewSet):
    serializer_class = NoticiaSerializer
    parser_classes = [MultiPartParser]
    pagination_class = PageNumberPagination

    def get_permissions(self) -> list[Any]:
        return {
            "list": [AllowAny()],
            "por_vertical": [AllowAny()],
            "retrieve": [IsAuthenticated()],
        }.get(self.action, [IsEditorOrAdmin(), IsAuthenticated()])

    def get_queryset(self) -> list[NoticiaSchema]:
        user: UserSchema = self.request.user
        queryset = NoticiaSchema.objects.all()

        # List e por_vertical retornam todas as noticias
        # Se for admin retorna todas
        if self.action in ["list", "por_vertical"] or user.role == UserRoleEnum.ADMIN:
            return queryset

        if self.action == "retrieve":
            # Se for leitor retorna apenas noticias publicadas
            if user.role == UserRoleEnum.READER:
                return queryset.filter(status=StatusNoticiaEnum.PUBLICADO)

            return queryset

        editando_noticia = self.action in ["update", "partial_update", "destroy"]
        if user.role == UserRoleEnum.EDITOR and editando_noticia:
            return queryset.filter(autor=user)

            # return base_query.filter(
            #     models.Q(is_pro=False) | models.Q(is_pro=True, verticais__in=user.user_plan.verticais.all())
            # ).distinct()

        return queryset.none()

    def create(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        try:
            return super().create(request, *args, **kwargs)
        except ImageError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        instance: NoticiaSchema = self.get_object()

        noticia_pro = instance.is_pro
        usuario_leitor = request.user.role == UserRoleEnum.READER
        plano_info = request.user.user_plan.plan == PlanEnum.JOTA_INFO

        if noticia_pro and usuario_leitor and plano_info:
            return Response(
                {"detail": "Acesso negado. Apenas usuário com plano JOTA PRO tem acesso a essa notícia."},
                status=status.HTTP_403_FORBIDDEN,
            )

        dentro_das_verticais_do_usuario = instance.verticais.filter(id__in=request.user.user_plan.verticais.all())
        if noticia_pro and not dentro_das_verticais_do_usuario:
            return Response(
                {
                    "detail": "Acesso negado. Usuário não tem permissão para acessar essa notícia. Verifique as verticais do plano.",
                    "Verticais_do_usuario": [vertical.name for vertical in request.user.user_plan.verticais.all()],
                    "Verticais_da_noticia": [vertical.name for vertical in instance.verticais.all()],
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["get"], url_path="(por-vertical/?P<vertical>[^/.]+)")  # type: ignore
    # def por_vertical(self, request: Request, vertical: str) -> None:
    #     """
    #     Retorna notícias por vertical
    #     Exemplo: /api/noticia/tributos/
    #     """
    #     vertical_validada = VerticalEnum.from_label(vertical.capitalize())
    #     if not vertical_validada:
    #         return Response(
    #             {
    #                 "detail": "Vertical não encontrada.",
    #                 "Verticais": VerticalEnum.labels,
    #             },
    #             status=404,
    #         )

    #     # Aplica o filtro de vertical
    #     queryset = self.filter_queryset(self.get_queryset())
    #     queryset = queryset.filter(verticais__name=vertical_validada.label)

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data, status.HTTP_200_OK)
