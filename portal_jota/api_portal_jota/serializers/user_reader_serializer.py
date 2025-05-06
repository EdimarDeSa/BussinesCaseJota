from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..enums.plan_enum import PlanEnum
from ..enums.user_role_enum import UserRoleEnum
from ..models import UserPlanSchema, UserSchema


class UserReaderSerializer(serializers.ModelSerializer):
    plan = serializers.SerializerMethodField(help_text="Plano do usuário")

    class Meta:
        model = UserSchema
        fields = ["id", "username", "email", "password", "role", "plan", "created_at", "updated_at"]
        extra_kwargs = {
            "id": {"read_only": True},
            "username": {"write_only": True, "required": True},
            "email": {"required": True},
            "password": {"write_only": True, "required": True, "style": {"input_type": "password"}},
            "role": {"read_only": True},
            "plan": {"read_only": True, "exemples": PlanEnum.JOTA_INFO.label},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data: dict) -> UserSchema:
        try:
            validated_data["password"] = make_password(validated_data["password"])

            validated_data["role"] = UserRoleEnum.READER

            user: UserSchema = super().create(validated_data)

            # Gera um plano inicial para o usuário
            UserPlanSchema.objects.create(
                cd_user=user,
                plan=PlanEnum.JOTA_INFO,
            )

            return user
        except Exception as e:
            raise serializers.ValidationError({"Erro ao criar usuário": str(e)})

    @extend_schema_field(serializers.CharField())
    def get_plan(self, instance: UserSchema) -> str:
        return instance.user_plan.get_plan_display() if hasattr(instance, "user_plan") else None

    def update(self, instance: UserSchema, validated_data: dict) -> UserSchema:
        validated_data.pop("role", None)

        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["role"] = instance.get_role_display()
        data["plan"] = self.get_plan(instance)
        return data
