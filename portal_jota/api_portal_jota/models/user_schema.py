import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.transaction import atomic

from ..enums.email_type_enum import EmailTypeEnum
from ..enums.user_role_enum import UserRoleEnum
from .user_plan_schema import UserPlanSchema


class UserSchema(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    role = models.CharField(max_length=1, choices=UserRoleEnum.choices, default=UserRoleEnum.READER)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        match self.role:
            case UserRoleEnum.ADMIN:
                return f"{self.username}: <Role: {self.role}>"
            case UserRoleEnum.EDITOR:
                return f"{self.username}: <Role: {self.role}>"
            case UserRoleEnum.READER:
                return f"{self.username}: <Role: {self.role}> - <Plan: {self.user_plan.plan} - Verticais: {self.user_plan.verticais.all()}>"

    @atomic
    def save(self, *args, **kwargs) -> None:
        is_new = self._state.adding

        super().save(*args, **kwargs)

        if is_new and self.role == UserRoleEnum.READER:
            self._create_user_plan()

        if is_new:
            from ..tasks.send_email import send_email

            send_email.delay(
                {
                    "email_type": EmailTypeEnum.BEM_VINDO,
                    "to": [str(self.id)],
                }
            )

    def _create_user_plan(self):
        UserPlanSchema.objects.create(cd_user=self)
