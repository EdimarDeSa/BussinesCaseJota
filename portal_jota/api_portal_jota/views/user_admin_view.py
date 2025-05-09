from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..permissions import IsAdmin
from ..serializers.user_admin_serializer import UserAdminSerializer


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
class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = UserSchema.objects.filter(role=UserRoleEnum.ADMIN)
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdmin, IsAuthenticated]
