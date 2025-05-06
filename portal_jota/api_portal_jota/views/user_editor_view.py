from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..permissions import IsSelfOrAdmin
from ..serializers.user_editor_serializer import UserEditorSerializer


class UserEditorViewSet(viewsets.ModelViewSet):
    serializer_class = UserEditorSerializer

    def get_queryset(self):
        if self.request.user.role == UserRoleEnum.ADMIN:
            return UserSchema.objects.filter(role=UserRoleEnum.EDITOR)

        return UserSchema.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), IsSelfOrAdmin()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSelfOrAdmin()]

        return super().get_permissions()
