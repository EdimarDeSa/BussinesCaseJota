from typing import Any

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from ..enums.user_role_enum import UserRoleEnum
from ..models import UserSchema
from ..serializers.user_serializer import UserSerializer


@receiver(post_migrate)  # type: ignore
def create_default_admin(sender: Any, **kwargs: dict) -> None:
    if sender.name != "api_portal_jota":
        return

    serializer = UserSerializer(
        data={
            "username": "admin",
            "email": "admin@example.com",
            "password": "P@s5W0rd",
            "role": UserRoleEnum.ADMIN.label,
        }
    )

    if serializer.is_valid():
        serializer.save()
