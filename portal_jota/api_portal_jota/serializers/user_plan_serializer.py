from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..enums.plan_enum import PlanEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import UserPlanSchema, VerticalSchema


class UserPlanSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="cd_user.id", read_only=True)
    user_name = serializers.CharField(source="cd_user.username", read_only=True)
    verticais = serializers.ListField(
        child=serializers.ChoiceField(choices=VerticalEnum.labels),
        required=False,
        write_only=True,
    )
    plan = serializers.ChoiceField(
        choices=PlanEnum.labels,
        required=True,
        help_text=f"Plano. Valores possíveis: {PlanEnum.labels}",
        write_only=True,
    )

    class Meta:
        model = UserPlanSchema

        fields = [
            "id",
            "plan",
            "user_id",
            "user_name",
            "verticais",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        plan_label = attrs.get("plan", None)

        if plan_label is not None:
            plan = PlanEnum.from_label(plan_label)
            if plan is None:
                raise serializers.ValidationError({"plan": f"Plano inválido. Valores possíveis: {PlanEnum.labels}"})

            attrs["plan"] = plan

            if plan == PlanEnum.JOTA_PRO and "verticais" not in attrs:
                raise serializers.ValidationError({"verticais": "Obrigatório para plano JOTA PRO."})

        return attrs

    def update(self, instance: UserPlanSchema, validated_data: dict) -> UserPlanSchema:
        verticais_data = validated_data.pop("verticais", None)

        instance = super().update(instance, validated_data)

        if instance.plan == PlanEnum.JOTA_PRO and verticais_data is not None:
            instance.verticais.set(VerticalSchema.objects.filter(name__in=verticais_data))

        return instance

    def to_representation(self, instance: UserPlanSchema) -> dict:
        data = super().to_representation(instance)
        data["verticais"] = [v.name for v in instance.verticais.all()]
        data["plan"] = instance.get_plan_display()
        return data
