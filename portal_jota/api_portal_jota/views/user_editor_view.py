from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..permissions import IsAdmin, IsSelfOrAdmin
from ..serializers.user_editor_serializer import UserEditorSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="id",
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.UUID,
            description="ID do usuário",
        )
    ]
)
class UserEditorViewSet(viewsets.ModelViewSet):
    serializer_class = UserEditorSerializer

    def get_queryset(self):
        if self.request.user.role == UserRoleEnum.ADMIN:
            return UserSchema.objects.filter(role=UserRoleEnum.EDITOR)

        return UserSchema.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsAdmin()]

        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), IsSelfOrAdmin()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSelfOrAdmin()]

        return super().get_permissions()
