from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..permissions import IsAdmin
from ..serializers.user_editor_serializer import UserEditorSerializer


class UserEditorViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserSchema.objects.filter(role=UserRoleEnum.EDITOR)
    serializer_class = UserEditorSerializer
    permission_classes = [IsAdmin, IsAuthenticated]
