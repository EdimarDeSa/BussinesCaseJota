from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..permissions import IsAdmin, IsSelfOrAdmin
from ..serializers.user_editor_serializer import UserEditorSerializer


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
class UserEditorViewSet(viewsets.ModelViewSet):
    serializer_class = UserEditorSerializer
    permission_classes = [IsAuthenticated]

    def get_action_permissions(self) -> list[Any]:
        return {
            "create": [IsAdmin()],
        }.get(self.action, [IsSelfOrAdmin()])

    def get_permissions(self) -> list[Any]:
        """Combina permissões base com as específicas da ação"""
        return super().get_permissions() + self.get_action_permissions()

    def get_queryset(self) -> None:
        if self.request.user.role == UserRoleEnum.ADMIN:
            return UserSchema.objects.filter(role=UserRoleEnum.EDITOR)

        return UserSchema.objects.filter(id=self.request.user.id)
