from typing import Any

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserRoleEnum.labels, required=False)

    class Meta:
        model = UserSchema

        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "created_at", "updated_at"]

        extra_kwargs = {"username": {"write_only": True}, "password": {"write_only": True}}

    def create(self, validated_data: dict) -> UserSchema:

        password = validated_data.pop("password")
        validate_password(password, UserSchema)
        validated_data["password"] = make_password(password)

        role = validated_data.pop("role")
        validated_data["role"] = UserRoleEnum.from_label(role)

        return super().create(validated_data)

    def update(self, instance: UserSchema, validated_data: dict) -> UserSchema:

        if "password" in validated_data:
            password = validated_data.pop("password")
            validate_password(password, UserSchema)

            validated_data["password"] = make_password(password)

        if "role" in validated_data:
            role = validated_data.pop("role")
            validated_data["role"] = UserRoleEnum.from_label(role)

        return super().update(instance, validated_data)

    def to_representation(self, instance: UserSchema) -> dict[str, Any]:
        rep = super().to_representation(instance)
        role = rep.pop("role")
        rep["role"] = instance.get_role_display()

        if role == UserRoleEnum.READER:
            rep["plan_id"] = instance.user_plan.id
            rep["plan"] = instance.user_plan.get_plan_display()

        return rep
