from django.db import models


class UserRoleEnum(models.TextChoices):
    ADMIN = "A", "Admin"
    EDITOR = "E", "Editor"
    READER = "R", "Leitor"
