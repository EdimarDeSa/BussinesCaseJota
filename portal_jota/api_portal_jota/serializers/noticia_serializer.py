from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..enums.plan_enum import PlanEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import NoticiaSchema, VerticalSchema


class NoticiaSerializer(serializers.ModelSerializer):
    verticais = serializers.ListField(
        child=serializers.ChoiceField(choices=VerticalEnum.labels),
        required=True,
        write_only=True,
        help_text=f"Lista de verticais. Valores possíveis: {[v.value for v in VerticalEnum]}",
    )

    class Meta:
        model = NoticiaSchema
        fields = [
            "id",
            "titulo",
            "subtitulo",
            "imagem",
            "conteudo",
            "data_publicacao",
            "autor",
            "status",
            "is_pro",
            "verticais",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "autor": {"read_only": True},
            "status": {"read_only": True},
            "imagem": {"required": False},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data):
        verticais = validated_data.pop("verticais")

        validated_data["autor"] = self.context["request"].user

        noticia = super().create(validated_data)

        verticais_objects = VerticalSchema.objects.filter(name__in=verticais)
        noticia.verticais.set(verticais_objects)
        return noticia

    def update(self, instance: NoticiaSchema, validated_data: dict) -> NoticiaSchema:
        validated_data.pop("autor", None)
        validated_data.pop("status", None)
        return super().update(instance, validated_data)

    @extend_schema_field(serializers.CharField())
    def get_autor_username(self, instance: NoticiaSchema) -> str:
        return instance.autor.username

    @extend_schema_field(serializers.CharField())
    def get_autor_id(self, instance: NoticiaSchema) -> str:
        return str(instance.autor.id)

    def to_representation(self, instance: NoticiaSchema) -> dict:
        data = super().to_representation(instance)
        data["autor_id"] = self.get_autor_id(instance)
        data["autor"] = self.get_autor_username(instance)
        data["status"] = instance.get_status_display()
        data["verticais"] = [v.name for v in instance.verticais.all()]
        return data
