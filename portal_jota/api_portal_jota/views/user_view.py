from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..permissions import IsSelfOrAdmin
from ..serializers.user_serializer import UserSerializer
from ..types import extend_uuid_schema


@extend_schema_view(**extend_uuid_schema(description="ID do usuário"))
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_permissions(self) -> list[BasePermission]:

        if self.action == "create":
            return [AllowAny()]

        return [IsAuthenticated(), IsSelfOrAdmin()]

    def get_queryset(self) -> list[UserSchema]:
        if self.request.user.is_authenticated:
            if self.request.user.role == UserRoleEnum.ADMIN:
                return UserSchema.objects.all()

            return UserSchema.objects.filter(id=self.request.user.id)

        return UserSchema.objects.none()

    def create(self, request: Request, *args: tuple, **kwargs: dict) -> Response:

        role = self.request.data.get("role")
        if role in [UserRoleEnum.ADMIN.label, UserRoleEnum.EDITOR.label]:
            if not self._check_user_has_permission(request):
                raise PermissionDenied({"role": f"Você não tem permissão para criar um {role}."})

        return super().create(request, *args, **kwargs)

    def update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        if self.request.data.get("role", False):
            if not self._check_user_has_permission(request):
                raise PermissionDenied({"role": "Você não tem permissão para editar permissões."})

        return super().update(request, *args, **kwargs)

    def partial_update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        if self.request.data.get("role", False):
            if not self._check_user_has_permission(request):
                raise PermissionDenied({"role": "Você não tem permissão para editar permissões."})

        return super().partial_update(request, *args, **kwargs)

    def _check_user_has_permission(self, request: Request) -> bool:
        user = request.user

        if not user.is_authenticated:
            return False
        return user.role == UserRoleEnum.ADMIN
