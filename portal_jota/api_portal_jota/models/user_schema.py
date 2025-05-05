import uuid

from django.db import models

from ..enums.user_role_enum import UserRoleEnum


class UserSchema(models.Model):
    id_user = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, name="id")
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=50)
    role = models.CharField(max_length=1, choices=UserRoleEnum.choices, default=UserRoleEnum.READER)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
