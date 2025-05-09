from os import read

from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..enums.plan_enum import PlanEnum
from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema


class UserReaderSerializer(serializers.ModelSerializer):
    plan_id = serializers.UUIDField(source="user_plan.id", read_only=True)
    plan = serializers.CharField(source="user_plan.get_plan_display", read_only=True)
    role = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = UserSchema

        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "plan_id",
            "plan",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "created_at", "updated_at"]

        extra_kwargs = {"username": {"write_only": True}, "password": {"write_only": True}}

    def create(self, validated_data: dict) -> UserSchema:
        validated_data["password"] = make_password(validated_data["password"])

        validated_data["role"] = UserRoleEnum.READER

        return super().create(validated_data)

    def update(self, instance: UserSchema, validated_data: dict) -> UserSchema:

        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        return super().update(instance, validated_data)
