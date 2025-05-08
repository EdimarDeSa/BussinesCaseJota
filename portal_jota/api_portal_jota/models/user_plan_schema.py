import uuid

from django.db import models

from ..enums.plan_enum import PlanEnum


class UserPlanSchema(models.Model):
    id_user_plan = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, name="id")
    plan = models.CharField(max_length=1, choices=PlanEnum.choices, default=PlanEnum.JOTA_INFO)
    cd_user = models.OneToOneField("UserSchema", on_delete=models.CASCADE, related_name="user_plan")
    verticais = models.ManyToManyField("VerticalSchema", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plano: {self.get_plan_display()} de {self.cd_user.username}"
