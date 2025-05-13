from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..enums.status_noticia_imagem_enum import StatusNoticiaImagemEnum
from ..enums.vertical_enum import VerticalEnum
from ..models import NoticiaSchema, VerticalSchema


class NoticiaSerializer(serializers.ModelSerializer):
    verticais = serializers.ListField(
        child=serializers.ChoiceField(choices=VerticalEnum.labels),
        required=True,
        write_only=True,
        help_text=f"Lista de verticais. Valores possíveis: {VerticalEnum.labels}",
    )
    imagem_url = serializers.SerializerMethodField(read_only=True)
    autor_id = serializers.UUIDField(source="autor.id", read_only=True)
    autor_username = serializers.CharField(source="autor.username", read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = NoticiaSchema

        fields = [
            "id",
            "titulo",
            "subtitulo",
            "imagem",
            "imagem_url",
            "status_imagem",
            "conteudo",
            "data_publicacao",
            "autor_username",
            "autor_id",
            "status",
            "is_pro",
            "verticais",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "created_at", "updated_at"]

    @extend_schema_field(serializers.URLField)  # type: ignore
    def get_imagem_url(self, instance: NoticiaSchema) -> str | None:
        if instance.status_imagem == StatusNoticiaImagemEnum.OK:
            return instance.imagem.url
        return None

    def create(self, validated_data: dict) -> NoticiaSchema:
        verticais = validated_data.pop("verticais")
        validated_data["autor"] = self.context["request"].user

        noticia = super().create(validated_data)

        verticais_objects = VerticalSchema.objects.filter(name__in=verticais)
        noticia.verticais.set(verticais_objects)
        return noticia

    def to_representation(self, instance: NoticiaSchema) -> dict:
        verticais = [v.name for v in instance.verticais.all()]
        action = self.context.get("view").action
        representation = super().to_representation(instance)
        representation["verticais"] = verticais

        if action not in ["por_vertical", "list"]:
            # Retorno completo para outras ações
            return representation

        [
            representation.pop(f)
            for f in [
                "id",
                "titulo",
                "subtitulo",
                "data_publicacao",
                "autor_username",
                "autor_id",
                "is_pro",
                "verticais",
            ]
        ]

        # Retorno reduzido para por_vertical e listagem
        return representation
