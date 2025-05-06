from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

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

    @extend_schema_field(serializers.CharField())
    def get_user(self, instance: UserPlanSchema) -> str:
        return instance.cd_user.get_username_display()

    def to_representation(self, instance: UserPlanSchema) -> dict:
        data = super().to_representation(instance)
        data["user"] = self.get_user(instance)
        return data
