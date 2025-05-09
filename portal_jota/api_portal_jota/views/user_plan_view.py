from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, viewsets
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
            description="ID do plano do usuário",
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

    def get_queryset(self):
        if self.request.user.role == UserRoleEnum.ADMIN:
            return UserPlanSchema.objects.all()

        return UserPlanSchema.objects.filter(cd_user=self.request.user.id)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), IsReaderOrdAdmin()]

        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsAdmin()]

        return super().get_permissions()
