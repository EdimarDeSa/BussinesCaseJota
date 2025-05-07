from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..enums.plan_enum import PlanEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import UserPlanSchema, VerticalSchema


class UserPlanSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(
        read_only=True,
    )
    verticais = serializers.ListField(
        child=serializers.ChoiceField(choices=VerticalEnum.labels),
        required=False,
        write_only=True,
        help_text=f"Lista de verticais. Valores possíveis: {[v.value for v in VerticalEnum]}",
    )

    class Meta:
        model = UserPlanSchema
        fields = ["id", "plan", "cd_user", "user", "verticais", "created_at", "updated_at"]
        extra_kwargs = {
            "id": {"read_only": True},
            "cd_user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def validate(self, attrs):
        if "plan" in attrs and attrs["plan"] == PlanEnum.JOTA_PRO:
            if "verticais" not in attrs:
                raise serializers.ValidationError(
                    {"verticais": "Este campo é obrigatório quando o plano for JOTA PRO."}
                )
        return super().validate(attrs)

    def update(self, instance: UserPlanSchema, validated_data: dict) -> UserPlanSchema:

        verticais_data = validated_data.pop("verticais", None)

        instance = super().update(instance, validated_data)

        if instance.plan == PlanEnum.JOTA_PRO and verticais_data is not None:
            instance.verticais.set(VerticalSchema.objects.filter(name__in=verticais_data))

        return instance

    @extend_schema_field(serializers.CharField())
    def get_user(self, instance: UserPlanSchema) -> str:
        return instance.cd_user.username

    def to_representation(self, instance: UserPlanSchema) -> dict:
        data = super().to_representation(instance)
        data["user"] = self.get_user(instance)
        data["plan"] = instance.get_plan_display()
        data["verticais"] = [v.name for v in instance.verticais.all()]
        return data
