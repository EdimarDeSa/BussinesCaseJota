from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserPlanSchema
from ..permissions import IsAdmin, IsReaderOrdAdmin
from ..serializers.user_plan_serializer import UserPlanSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="id",
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.UUID,
            description="ID do plano",
        )
    ]
)
class UserPlanViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    serializer_class = UserPlanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_action_permissions(self) -> list[Any]:
        return {
            "update": [IsAdmin()],
            "partial_update": [IsAdmin()],
            "list": [IsReaderOrdAdmin()],
            "retrieve": [IsReaderOrdAdmin()],
        }.get(self.action, [])

    def get_permissions(self) -> list[Any]:
        """Combina permissões base com as específicas da ação"""
        return super().get_permissions() + self.get_action_permissions()

    def get_queryset(self) -> UserPlanSchema:
        base_queryset = UserPlanSchema.objects.all()
        if self.request.user.role == UserRoleEnum.ADMIN:
            return base_queryset

        return base_queryset.filter(cd_user=self.request.user.id)
