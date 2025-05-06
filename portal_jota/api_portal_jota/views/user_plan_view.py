from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserPlanSchema
from ..permissions import IsAdmin, IsSelfOrAdmin
from ..serializers.user_plan_serializer import UserPlanSerializer


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
            return [IsAuthenticated(), IsSelfOrAdmin()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSelfOrAdmin()]

        return super().get_permissions()
