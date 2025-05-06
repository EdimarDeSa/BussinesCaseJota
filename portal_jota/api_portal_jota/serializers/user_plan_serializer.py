from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserPlanSchema


class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlanSchema
        fields = ["id", "plan", "cd_user", "categorias", "created_at", "updated_at"]
        extra_kwargs = {
            "id": {"read_only": True},
            "cd_user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def update(self, instance: UserPlanSchema, validated_data: dict) -> UserPlanSchema:
        validated_data.pop("cd_user", None)

        return super().update(instance, validated_data)
