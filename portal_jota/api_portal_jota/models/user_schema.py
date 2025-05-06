import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from ..enums.user_role_enum import UserRoleEnum


class UserSchema(AbstractUser):
    id_user = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, name="id")
    role = models.CharField(max_length=1, choices=UserRoleEnum.choices, default=UserRoleEnum.READER)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name()}: <Role: {self.role}>"
