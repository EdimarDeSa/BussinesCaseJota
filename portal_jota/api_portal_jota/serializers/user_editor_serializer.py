from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema


class UserEditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSchema
        fields = ["id", "username", "email", "password", "role", "created_at", "updated_at"]
        extra_kwargs = {
            "id": {"read_only": True},
            "username": {"write_only": True, "required": True},
            "password": {"write_only": True, "required": True, "style": {"input_type": "password"}},
            "role": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data: dict) -> UserSchema:
        validated_data["password"] = make_password(validated_data["password"])

        validated_data["role"] = UserRoleEnum.EDITOR

        return super().create(validated_data)

    def update(self, instance: UserSchema, validated_data: dict) -> UserSchema:
        validated_data.pop("role", None)

        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        return super().update(instance, validated_data)

    def to_representation(self, instance: UserSchema) -> dict:
        data = super().to_representation(instance)
        data["role"] = instance.get_role_display()
        return data
