from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..permissions import IsSelfOrAdmin
from ..serializers.user_reader_serializer import UserReaderSerializer


@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="ID do usuário",
            )
        ]
    )
)
class UserReaderViewSet(viewsets.ModelViewSet):
    serializer_class = UserReaderSerializer

    def get_action_permissions(self) -> list[Any]:
        return {
            "create": [AllowAny()],
        }.get(self.action, [IsAuthenticated(), IsSelfOrAdmin()])

    def get_permissions(self) -> list[Any]:
        """Combina permissões base com as específicas da ação"""
        return self.get_action_permissions()

    def get_queryset(self) -> UserSchema:
        base_queryset = UserSchema.objects.filter(role=UserRoleEnum.READER)

        if self.request.user.role == UserRoleEnum.READER:
            return base_queryset.filter(id=self.request.user.id)

        return base_queryset
